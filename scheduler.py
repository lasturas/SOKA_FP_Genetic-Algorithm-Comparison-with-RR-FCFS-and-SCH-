import asyncio
import httpx
import time
from datetime import datetime
import csv
import pandas as pd
import sys
import os
from dotenv import load_dotenv
from collections import namedtuple
import numpy as np
from algorithms import SchedulerAlgorithms 

# --- KONFIGURASI LINGKUNGAN ---
load_dotenv()
VM_SPECS = {
    'vm1': {'ip': os.getenv("VM1_IP"), 'cpu': 1}, 
    'vm2': {'ip': os.getenv("VM2_IP"), 'cpu': 2},
    'vm3': {'ip': os.getenv("VM3_IP"), 'cpu': 4}, 
    'vm4': {'ip': os.getenv("VM4_IP"), 'cpu': 8},
}
VM_PORT = 5000

# ==========================================
# KONFIGURASI PENGUJIAN
# ==========================================
DATASET_FILES = [
    'RandomSimpleDatase.txt',      
    'RandomStratifiedDataset.txt',
    'LowHighDataset.txt'
]
NUM_EXPERIMENTS = 10    # 10x Loop per Algoritma
# ==========================================

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])

def load_tasks(dataset_path: str) -> list[Task]:
    if not os.path.exists(dataset_path):
        print(f"[ERROR] File {dataset_path} TIDAK DITEMUKAN!")
        return []
    tasks = []
    with open(dataset_path, 'r') as f:
        for i, line in enumerate(f):
            try:
                line = line.strip()
                if not line: continue
                index = int(line)
                cpu_load = (index ** 2) * 10000
                tasks.append(Task(id=i, name=f"task-{index}-{i}", index=index, cpu_load=cpu_load))
            except ValueError: continue
    return tasks

async def execute_task_on_vm(task: Task, vm: VM, client: httpx.AsyncClient, 
                             vm_semaphore: asyncio.Semaphore, results_list: list):
    url = f"http://{vm.ip}:{VM_PORT}/task/{task.index}"
    task_exec_time = 0.0
    task_wait_time = 0.0
    wait_start = time.monotonic()
    MAX_RETRIES = 3
    
    try:
        async with vm_semaphore:
            task_wait_time = time.monotonic() - wait_start
            
            # --- UPDATE: PRINT SAAT MENGIRIM (Supaya tidak hening) ---
            print(f"    -> Mengirim {task.name} ke {vm.name}...", end=" ", flush=True)
            
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    await asyncio.sleep(0.2 * attempt)
                    start_exec = time.monotonic()
                    
                    # Timeout panjang
                    response = await client.get(url, timeout=300.0)
                    
                    if response.status_code == 200:
                        task_exec_time = time.monotonic() - start_exec
                        # --- UPDATE: PRINT SAAT SUKSES ---
                        print(f"OK ({task_exec_time:.2f}s)")
                        break 
                    elif response.status_code == 500:
                        if attempt == MAX_RETRIES:
                            print(f"GAGAL (500)")
                            task_exec_time = 0
                        else:
                            print(f"Retry...", end=" ", flush=True)
                    else:
                        print(f"Status {response.status_code}")
                        task_exec_time = 0; break
                except Exception as e:
                    if attempt == MAX_RETRIES: 
                        print(f"ERR Koneksi")
                        task_exec_time = 0
    except Exception:
        task_exec_time = 0
    finally:
        results_list.append({
            "task_id": task.id, "vm_assigned": vm.name, 
            "exec_time": task_exec_time, "wait_time": task_wait_time
        })

def calculate_metrics(results_list: list, vms: list[VM], total_time: float, algo_name: str, dataset_name: str, run_id: int):
    if not results_list: return None
    df = pd.DataFrame(results_list)
    success_df = df[df['exec_time'] > 0].copy()
    
    if success_df.empty: 
        return {
            "Run_ID": run_id, "Dataset": dataset_name, "Algorithm": algo_name,
            "Makespan": 0, "Throughput": 0, "Resource_Utilization": 0, "Imbalance_Degree": 0,
            "Total_Tasks_Success": 0, "Total_CPU_Time": 0, "Total_Wait_Time": 0,
            "Avg_Start_Time": 0, "Avg_Execution_Time": 0, "Avg_Finish_Time": 0
        }

    # Hitung 10 Parameter
    makespan = total_time
    total_tasks_success = len(success_df)
    throughput = total_tasks_success / makespan if makespan > 0 else 0
    total_cpu_time = success_df['exec_time'].sum()
    total_wait_time = success_df['wait_time'].sum()
    avg_start_time = success_df['wait_time'].mean()
    avg_exec_time = success_df['exec_time'].mean()
    avg_finish_time = (success_df['wait_time'] + success_df['exec_time']).mean()
    
    total_cores = sum(vm.cpu_cores for vm in vms)
    utilization = (total_cpu_time / (makespan * total_cores)) * 100
    
    vm_loads = success_df.groupby('vm_assigned')['exec_time'].sum()
    if not vm_loads.empty:
        avg_load = vm_loads.mean()
        imbalance = (vm_loads.max() - vm_loads.min()) / avg_load if avg_load > 0 else 0
    else:
        imbalance = 0
    
    return {
        "Run_ID": run_id, "Dataset": dataset_name, "Algorithm": algo_name,
        "Makespan": makespan, "Throughput": throughput, "Resource_Utilization": utilization,
        "Imbalance_Degree": imbalance, "Total_Tasks_Success": total_tasks_success,
        "Total_CPU_Time": total_cpu_time, "Total_Wait_Time": total_wait_time,
        "Avg_Start_Time": avg_start_time, "Avg_Execution_Time": avg_exec_time,
        "Avg_Finish_Time": avg_finish_time
    }

async def run_cycle(run_id: int, dataset: str, algo_name: str, tasks: list, vms: list):
    scheduler = SchedulerAlgorithms(vms)
    assignment = {}
    try:
        if algo_name == 'Round-Robin': assignment = scheduler.schedule_round_robin(tasks)
        elif algo_name == 'FCFS': assignment = scheduler.schedule_fcfs(tasks)
        elif algo_name == 'SHC': assignment = scheduler.schedule_stochastic_hill_climbing(tasks, iterations=500)
        elif algo_name == 'GA/ErWCA': assignment = scheduler.schedule_erwca(tasks, k_best=2)
    except Exception: return None

    results = []
    # Semaphore 1 untuk keamanan
    semaphores = {vm.name: asyncio.Semaphore(1) for vm in vms} 
    tasks_dict = {t.id: t for t in tasks}
    vms_dict = {v.name: v for v in vms}
    
    start_t = time.monotonic()
    async with httpx.AsyncClient() as client:
        coroutines = []
        for tid, vm_name in assignment.items():
            if tid in tasks_dict and vm_name in vms_dict:
                coroutines.append(execute_task_on_vm(
                    tasks_dict[tid], vms_dict[vm_name], client, semaphores[vm_name], results
                ))
        await asyncio.gather(*coroutines)
    
    total_t = time.monotonic() - start_t
    return calculate_metrics(results, vms, total_t, algo_name, dataset, run_id)

async def main():
    print(f"\n=== MEMULAI PENGUJIAN LENGKAP (REAL-TIME LOG) ===")
    vms = [VM(n, s['ip'], s['cpu']) for n, s in VM_SPECS.items()]
    algorithms = ['Round-Robin', 'FCFS', 'SHC', 'GA/ErWCA']
    global_results_buffer = []
    
    for dataset_file in DATASET_FILES:
        print(f"\n{'='*60}")
        print(f"DATASET: {dataset_file}")
        print(f"{'='*60}")
        tasks = load_tasks(dataset_file)
        if not tasks: continue
        
        for algo in algorithms:
            print(f"\n>>> Algoritma: {algo} (10x Loop)")
            current_algo_results = []
            
            for i in range(1, NUM_EXPERIMENTS + 1):
                print(f"\n[Loop {i}/{NUM_EXPERIMENTS}]")
                await asyncio.sleep(0.5)
                res = await run_cycle(i, dataset_file, algo, tasks, vms)
                if res: 
                    current_algo_results.append(res)
                    print(f"    => Selesai! Makespan: {res['Makespan']:.2f}s")
                else:
                    print("    => Error!")
            
            if current_algo_results:
                clean_algo = algo.replace("/", "_") 
                clean_data = dataset_file.replace(".txt", "")
                filename = f"LOG_{clean_data}_{clean_algo}.csv"
                pd.DataFrame(current_algo_results).to_csv(filename, index=False)
                print(f"    [SAVED] {filename}")
                global_results_buffer.extend(current_algo_results)
                
    if global_results_buffer:
        print("\n" + "="*80)
        print("MENGHITUNG FINAL SUMMARY...")
        df_global = pd.DataFrame(global_results_buffer)
        df_global.to_csv("FINAL_ALL_RAW_DATA.csv", index=False)
        
        summary = df_global.groupby(['Dataset', 'Algorithm']).mean(numeric_only=True).reset_index()
        summary = summary.sort_values(by=['Dataset', 'Resource_Utilization'], ascending=[True, False])
        summary.to_csv("FINAL_AVERAGE_SUMMARY.csv", index=False)
        
        print(f"FILE OUTPUT: FINAL_AVERAGE_SUMMARY.csv")
        print("="*80)

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDIHENTIKAN.")
    except Exception as e:
        print(f"FATAL: {e}")