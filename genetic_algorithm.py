import random
import time
import math

# --- Parameter Konfigurasi GA ---
POPULATION_SIZE = 150   # 1-100
MAX_GENERATIONS = 300   # 1-200
MUTATION_RATE = 0.05
CROSSOVER_RATE = 0.8
TOURNAMENT_SIZE = 5
ELITISM_COUNT = 2

class Chromosome:
    def __init__(self, gene):
        self.gene = gene
        self.fitness = float('inf')

def schedule(tasks, vms, iterations):
    """
    Fungsi utama GA yang dipanggil oleh scheduler.py.
    Nama parameter disesuaikan dengan panggilan di scheduler.py (tasks, vms, iterations).
    Parameter 'iterations' tidak digunakan di GA, tapi kita terima agar signature-nya cocok.
    """
    num_tasks = len(tasks)
    num_vms = len(vms)

    print("Memulai Algoritma Genetika...")
    start_time = time.time()

    population = initialize_population(num_tasks, num_vms)
    best_overall_solution = None
    best_overall_fitness = float('inf')

    for generation in range(MAX_GENERATIONS):
        evaluate_population(population, tasks, vms)

        current_best = min(population, key=lambda chrom: chrom.fitness)
        if current_best.fitness < best_overall_fitness:
            best_overall_fitness = current_best.fitness
            best_overall_solution = current_best

        if generation % 20 == 0:
            print(f"Generasi-{generation} - Best Fitness (Makespan Perkiraan): {best_overall_fitness:.4f}s")
        
        new_population = []
        population.sort(key=lambda chrom: chrom.fitness)
        new_population.extend(population[:ELITISM_COUNT])

        while len(new_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)

            if random.random() < CROSSOVER_RATE:
                child1_gene, child2_gene = crossover(parent1.gene, parent2.gene)
                children_genes = [child1_gene, child2_gene]
            else:
                children_genes = [parent1.gene, parent2.gene]

            for gene in children_genes:
                mutated_gene = mutate(gene, num_vms)
                new_population.append(Chromosome(mutated_gene))
                if len(new_population) >= POPULATION_SIZE:
                    break
        
        population = new_population

    end_time = time.time()
    print(f"Algoritma Genetika selesai dalam {end_time - start_time:.4f} detik.")

    # Konversi hasil terbaik ke format yang dibutuhkan: {task.id: vm.name}
    final_assignment = {}
    if best_overall_solution:
        for i, task in enumerate(tasks):
            vm_index = best_overall_solution.gene[i]
            final_assignment[task.id] = vms[vm_index].name
    
    return final_assignment

def initialize_population(num_tasks, num_vms):
    return [Chromosome([random.randint(0, num_vms - 1) for _ in range(num_tasks)]) for _ in range(POPULATION_SIZE)]

def evaluate_population(population, tasks, vms):
    for chrom in population:
        chrom.fitness = evaluate_solution(chrom.gene, tasks, vms)

def evaluate_solution(solution_gene, tasks, vms):
    """Fungsi Fitness yang menghitung perkiraan makespan."""
    vm_loads = [0.0] * len(vms)
    for i, task in enumerate(tasks):
        vm_index = solution_gene[i]
        # Menggunakan cpu_load yang sudah dihitung sebelumnya di scheduler.py
        vm_loads[vm_index] += task.cpu_load
    
    execution_times = [vm_loads[i] / vms[i].cpu_cores for i in range(len(vms))]
    
    # Hitung Makespan: waktu selesai dari VM yang paling lama bekerja
    makespan = max(execution_times) if execution_times else 0

    # --- BAGIAN YANG PERLU DITAMBAHKAN ---
    # Hitung Imbalance berdasarkan waktu eksekusi
    if len(vms) > 0:
        mean_exec_time = sum(execution_times) / len(vms)
        # Variance adalah rata-rata dari kuadrat selisih setiap waktu dengan rata-ratanya
        variance = sum([(t - mean_exec_time) ** 2 for t in execution_times]) / len(vms)
        imbalance = math.sqrt(variance) # Imbalance di sini adalah standard deviation
    else:
        imbalance = 0
    # ------------------------------------
    
    # Inilah baris return yang menggabungkan keduanya.
    # Kamu bisa bereksperimen dengan bobot '2.0' ini.
    return makespan + (imbalance * 100.0) 


def tournament_selection(population):
    tournament = random.sample(population, TOURNAMENT_SIZE)
    return min(tournament, key=lambda chrom: chrom.fitness)

def crossover(parent1_gene, parent2_gene):
    size = len(parent1_gene)
    if size <= 1: return parent1_gene, parent2_gene
    
    cx_point = random.randint(1, size - 1)
    
    child1_gene = parent1_gene[:cx_point] + parent2_gene[cx_point:]
    child2_gene = parent2_gene[:cx_point] + parent1_gene[cx_point:]
    
    return child1_gene, child2_gene

def mutate(gene, num_vms):
    mutated_gene = list(gene)
    for i in range(len(mutated_gene)):
        if random.random() < MUTATION_RATE:
            mutated_gene[i] = random.randint(0, num_vms - 1)
    return mutated_gene