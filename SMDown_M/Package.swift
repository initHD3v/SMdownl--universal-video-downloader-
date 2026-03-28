// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "SMDown_M",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "SMDown_M",
            targets: ["SMDown_M"]),
    ],
    dependencies: [
        .package(url: "https://github.com/onevcat/Kingfisher.git", from: "8.0.0"),
        .package(url: "https://github.com/kareman/SwiftShell.git", from: "5.1.0"),
    ],
    targets: [
        .target(
            name: "SMDown_M",
            dependencies: [
                .product(name: "Kingfisher", package: "Kingfisher"),
                .product(name: "SwiftShell", package: "SwiftShell")
            ],
            path: "SMDown_M"),
        .testTarget(
            name: "SMDown_MTests",
            dependencies: ["SMDown_M"],
            path: "SMDown_MTests"),
    ]
)
