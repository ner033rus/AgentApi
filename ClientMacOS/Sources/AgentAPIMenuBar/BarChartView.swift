import AppKit

/// Четыре мини-столбика: CPU, RAM, GPU, Ollama (доля RAM под Ollama).
final class BarChartView: NSView {
    var metrics: DisplayMetrics = .offline {
        didSet { needsDisplay = true }
    }

    private let barCount = 4
    private let pad: CGFloat = 2
    private let gap: CGFloat = 2

    override var intrinsicContentSize: NSSize {
        NSSize(width: 52, height: 18)
    }

    override func draw(_ dirtyRect: NSRect) {
        super.draw(dirtyRect)
        let bounds = self.bounds
        let h = bounds.height - pad * 2
        let totalW = bounds.width - pad * 2
        let barW = (totalW - CGFloat(barCount - 1) * gap) / CGFloat(barCount)
        let x0 = pad

        let cpuH = height(for: metrics.cpu)
        let ramH = height(for: metrics.ram)
        let gpuH: CGFloat = {
            if !metrics.reachable { return 0 }
            if let u = metrics.gpuUtil { return height(for: u) }
            if metrics.gpuAvailable { return height(for: 0) }
            return h * 0.12
        }()
        let olH = height(for: metrics.ollamaRamPercent)

        let values: [(CGFloat, NSColor)] = [
            (cpuH, NSColor.systemCyan),
            (ramH, NSColor.systemGreen),
            (gpuH, gpuBarColor()),
            (olH, NSColor.systemPurple),
        ]

        for i in 0 ..< barCount {
            let x = x0 + CGFloat(i) * (barW + gap)
            let rect = NSRect(x: x, y: pad, width: barW, height: h)
            NSColor.separatorColor.withAlphaComponent(0.35).setFill()
            NSBezierPath(roundedRect: rect, xRadius: 1.5, yRadius: 1.5).fill()

            let fillH = max(1, values[i].0)
            let fillRect = NSRect(x: x, y: pad, width: barW, height: fillH)
            values[i].1.setFill()
            NSBezierPath(roundedRect: fillRect, xRadius: 1.2, yRadius: 1.2).fill()
        }

        if !metrics.reachable {
            NSColor.systemRed.withAlphaComponent(0.85).setFill()
            let dot = NSRect(x: bounds.maxX - 5, y: bounds.maxY - 5, width: 4, height: 4)
            NSBezierPath(ovalIn: dot).fill()
        }
    }

    private func gpuBarColor() -> NSColor {
        if !metrics.reachable { return NSColor.systemOrange }
        if metrics.gpuUtil != nil { return NSColor.systemOrange }
        if metrics.gpuAvailable { return NSColor.systemOrange.withAlphaComponent(0.35) }
        return NSColor.tertiaryLabelColor
    }

    private func height(for percent: Double) -> CGFloat {
        let bounds = self.bounds
        let h = max(0, bounds.height - pad * 2)
        return CGFloat(percent / 100.0) * h
    }
}
