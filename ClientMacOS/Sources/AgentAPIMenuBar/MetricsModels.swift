import Foundation

/// Ответ `GET /api/v1/metrics` (см. Server/app/models/schemas.py).
struct MetricsPayload: Codable {
    let cpu: CpuBlock
    let ram: RamBlock
    let gpu: GpuBlock
    let ollama: OllamaBlock
}

struct CpuBlock: Codable {
    let percent: Double
}

struct RamBlock: Codable {
    let percent: Double
    let usedBytes: Int64
    let totalBytes: Int64

    enum CodingKeys: String, CodingKey {
        case percent
        case usedBytes = "used_bytes"
        case totalBytes = "total_bytes"
    }
}

struct GpuBlock: Codable {
    let available: Bool?
    let utilPercent: Double?
    let memoryUsedMib: Double?
    let memoryTotalMib: Double?

    enum CodingKeys: String, CodingKey {
        case available
        case utilPercent = "util_percent"
        case memoryUsedMib = "memory_used_mib"
        case memoryTotalMib = "memory_total_mib"
    }
}

struct OllamaBlock: Codable {
    let processes: [OllamaProcessRow]
}

struct OllamaProcessRow: Codable {
    let memoryBytes: Int64

    enum CodingKeys: String, CodingKey {
        case memoryBytes = "memory_bytes"
    }
}

struct DisplayMetrics {
    /// 0…100
    let cpu: Double
    let ram: Double
    /// 0…100, при недоступной GPU — nil
    let gpuUtil: Double?
    let gpuAvailable: Bool
    /// Занятость VRAM (Memory-Usage), 0…100; nil если нет данных nvidia-smi
    let gpuMemoryPercent: Double?
    let reachable: Bool
}

extension DisplayMetrics {
    static let offline = DisplayMetrics(
        cpu: 0,
        ram: 0,
        gpuUtil: nil,
        gpuAvailable: false,
        gpuMemoryPercent: nil,
        reachable: false
    )
}
