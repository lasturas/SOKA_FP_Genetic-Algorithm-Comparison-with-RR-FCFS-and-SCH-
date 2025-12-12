# Analisis Komparatif Algoritma Penjadwalan Tugas Cloud Computing
**Genetic Algorithm (GA) vs Round Robin (RR) vs FCFS vs Stochastic Hill Climbing (SHC)**

![Language](https://img.shields.io/badge/Language-Python%20%7C%20Java-blue)
![Environment](https://img.shields.io/badge/Environment-Docker%20%7C%20CloudSim-orange)
![Subject](https://img.shields.io/badge/Course-Strategi%20Optimasi%20Komputasi%20Awan-green)

> **Project Akhir Mata Kuliah Strategi Optimasi Komputasi Awan (SOKA) - Kelas B**  
> Departemen Teknologi Informasi, Institut Teknologi Sepuluh Nopember (ITS).

## 📋 Gambaran Umum (Overview)
Repository ini berisi implementasi dan analisis perbandingan kinerja algoritma penjadwalan tugas (*task scheduling*) pada lingkungan komputasi awan yang heterogen. Penelitian ini membandingkan algoritma evolusioner **Genetic Algorithm (GA)** melawan algoritma konvensional dan heuristik lainnya untuk mengoptimalkan waktu penyelesaian (*Makespan*), *Throughput*, dan keseimbangan beban (*Load Balancing*).

Pengujian dilakukan pada dua lingkungan:
1.  **Real Testbed:** Implementasi nyata menggunakan **Python & Docker Container** pada klaster server heterogen.
2.  **Simulation:** Simulasi skala besar menggunakan **CloudSim (Java)** dengan dataset *Real World Trace* (SDSC).

## 🚀 Algoritma yang Diuji
1.  **Genetic Algorithm (GA):** Algoritma evolusioner yang diusulkan untuk optimasi global dan mencegah *server crash*.
2.  **Round Robin (RR):** Algoritma statis siklik (sebagai baseline).
3.  **First Come First Serve (FCFS):** Algoritma antrian sederhana.
4.  **Stochastic Hill Climbing (SHC):** Algoritma pencarian lokal heuristik.

## 📊 Hasil Utama (Key Findings)
Berdasarkan eksperimen menggunakan dataset *Random Simple*, *Stratified*, *Low-High*, dan *SDSC Trace*:

*   **Robustness:** Pada skenario beban ekstrem (*Low-High*), algoritma statis (RR & FCFS) mengalami tingkat kegagalan (**Failure Rate**) hingga **26%** akibat *server overload* (HTTP 500). **GA** mempertahankan tingkat keberhasilan **>94%**.
*   **Efisiensi Waktu:** GA mencatat waktu penyelesaian (*Makespan*) tercepat, meningkatkan efisiensi waktu sebesar **5.3%** dibandingkan RR pada dataset SDSC.
*   **Resource Utilization:** GA mampu mendongkrak penggunaan CPU hingga **15.8%** lebih efisien dibandingkan metode statis pada lingkungan heterogen.

## 📂 Struktur Project

### 1. Real Environment (Python/Docker)
Implementasi REST API sederhana untuk mensimulasikan worker node.
*   `scheduler.py`: Driver utama pengujian (klien).
*   `algorithms.py`: Implementasi logika FCFS, RR, dan SHC.
*   `genetic_algorithm.py`: Implementasi logika Genetic Algorithm.
*   `datasets/`: File teks berisi beban kerja tugas.

### 2. Simulation (Java/CloudSim)
Validasi hasil menggunakan framework CloudSim.
*   `ExampleCloudsim.java`: Kode utama simulasi CloudSim.
*   `GeneticAlgorithm.java`: Implementasi GA dalam Java untuk CloudSim.

## 🛠️ Cara Menjalankan (How to Run)

### A. Real Environment (Python)
Pastikan Python 3.x dan library yang dibutuhkan terinstall (`httpx`, `pandas`, `numpy`, `dotenv`).

1. Konfigurasi file .env untuk IP VM/Docker Container.
2. Jalankan scheduler `python scheduler.py`.

### B. CloudSim Simulation (Java)
Project ini membutuhkan library **CloudSim 3.0.3**.
1.  Import project ke Eclipse/IntelliJ IDEA.
2.  Pastikan library CloudSim sudah ditambahkan ke *classpath*.
3.  Jalankan file `ExampleCloudsim.java`.

## 👥 Tim Penyusun (Group F)

| No | Nama | NRP |
| :--- | :--- | :--- |
| 1 | Riskiyatul Nur Oktarani | 5027231013 |
| 2 | Dian Anggraeni Putri | 5027231016 |
| 3 | Acintya Edria Sudarsono | 5027231020 |
| 4 | Tsaldia Hukma Cita | 5027231036 |
| 5 | Callista Meyra Azizah | 5027231060 |

