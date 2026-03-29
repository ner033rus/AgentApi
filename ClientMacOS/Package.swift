// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "AgentAPIMenuBar",
    platforms: [
        .macOS(.v13),
    ],
    products: [
        .executable(name: "AgentAPIMenuBar", targets: ["AgentAPIMenuBar"]),
    ],
    targets: [
        .executableTarget(
            name: "AgentAPIMenuBar",
            path: "Sources/AgentAPIMenuBar"
        ),
    ]
)
