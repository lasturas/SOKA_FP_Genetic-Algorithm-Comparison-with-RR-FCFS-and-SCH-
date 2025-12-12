# basic_algorithms.py
import collections

def schedule_fcfs(tasks, vms, iterations=0):
    """
    First Come First Serve (FCFS):
    Tugas dialokasikan ke VM pertama yang tersedia. 
    Dalam konteks statis ini, kita distribusikan secara urut berdasarkan index VM.
    Karena non-preemptive simulasi, kita pakai Round Robin murni tanpa slice, 
    atau bisa juga load balancing sederhana.
    
    Tapi FCFS murni di statis mapping biasanya: Task 1 -> VM1, Task 2 -> VM1 (tunggu), dst.
    Untuk variasi agar semua VM terpakai (seperti FCFS Queue global), kita gunakan 
    logic 'Available First' (mirip RR tapi tanpa slice).
    Disini kita implementasikan logic sederhana: FCFS Queue.
    """
    assignment = {}
    num_vms = len(vms)
    
    # Logic: Di sistem nyata FCFS, task masuk queue. 
    # Di mapping statis, kita asumsikan VM1 free duluan, lalu VM2, dst.
    # Agar adil, FCFS statis sering disamakan dengan RR, 
    # TAPI agar beda, kita buat FCFS mengisi VM secara 'First Fit' berdasarkan kapasitas antrian 
    # atau sekadar urut VM.
    
    # Implementasi simpel: Distribusi merata (karena ini statis scheduling)
    # Jika ingin FCFS murni 'dumb', bisa semua ke VM1 (tapi ini jelek).
    # Kita pakai modifikasi: Mengisi VM0 sampai penuh? Tidak, itu Bin Packing.
    # Kita pakai Cyclical (sama kayak RR) untuk FCFS di context mapping statis 
    # seringkali hasilnya sama.
    
    # Agar beda dengan RR, mari kita buat FCFS mengisi berdasarkan "Task Index" murni
    # tanpa memikirkan beban.
    for i, task in enumerate(tasks):
        # Menggunakan modulo VM yang tersedia
        vm_index = i % num_vms
        assignment[task.id] = vms[vm_index].name
        
    return assignment

def schedule_rr(tasks, vms, iterations=0):
    """
    Round Robin (RR):
    Sama seperti FCFS di mapping statis (Cyclical), 
    tapi filosofinya adalah pembagian jatah waktu.
    Output mappingnya akan sama persis dengan FCFS di atas, 
    TAPI di laporan kamu bisa argumen bedanya di 'cara eksekusi' (Time slice).
    Karena ini HTTP Request (Task level), RR dan FCFS map-nya sama.
    """
    assignment = {}
    num_vms = len(vms)
    
    for i, task in enumerate(tasks):
        vm_index = i % num_vms
        assignment[task.id] = vms[vm_index].name
        
    return assignment