import Foundation

enum MetricsClient {
    private static let session: URLSession = {
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 5
        config.timeoutIntervalForResource = 8
        return URLSession(configuration: config)
    }()

    static func baseURLString() -> String {
        let d = UserDefaults.standard
        if let s = d.string(forKey: Keys.serverBaseURL), !s.isEmpty {
            return s.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        return Keys.defaultBaseURL
    }

    static func setBaseURLString(_ value: String) {
        UserDefaults.standard.set(value, forKey: Keys.serverBaseURL)
    }

    static func fetchMetrics(baseURL: String) async -> DisplayMetrics {
        guard let url = makeMetricsURL(baseURL: baseURL) else {
            return .offline
        }
        do {
            let (data, response) = try await session.data(from: url)
            guard let http = response as? HTTPURLResponse, (200 ... 299).contains(http.statusCode) else {
                return .offline
            }
            let decoded = try JSONDecoder().decode(MetricsPayload.self, from: data)
            return map(decoded)
        } catch {
            return .offline
        }
    }

    private static func makeMetricsURL(baseURL: String) -> URL? {
        var trimmed = baseURL.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.hasSuffix("/") {
            trimmed.removeLast()
        }
        guard let root = URL(string: trimmed) else { return nil }
        return root.appendingPathComponent("api/v1/metrics")
    }

    private static func map(_ m: MetricsPayload) -> DisplayMetrics {
        let gpuAvail = m.gpu.available ?? true
        let gpuUtil = m.gpu.utilPercent
        let gpuMemPct: Double? = {
            guard gpuAvail, let u = m.gpu.memoryUsedMib, let t = m.gpu.memoryTotalMib, t > 0 else {
                return nil
            }
            return clampPercent(u / t * 100)
        }()
        return DisplayMetrics(
            cpu: clampPercent(m.cpu.percent),
            ram: clampPercent(m.ram.percent),
            gpuUtil: gpuUtil.map { clampPercent($0) },
            gpuAvailable: gpuAvail,
            gpuMemoryPercent: gpuMemPct,
            reachable: true
        )
    }

    private static func clampPercent(_ x: Double) -> Double {
        min(100, max(0, x))
    }
}

enum Keys {
    static let serverBaseURL = "AgentAPI.serverBaseURL"
    /// Совпадает с AGENT_API_PORT по умолчанию в Server/app/config.py
    static let defaultBaseURL = "http://192.168.1.146:8765"
}
