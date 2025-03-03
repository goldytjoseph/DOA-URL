# DOA-URL
A lightweight, fast, and concurrent HTTP probe utility for checking if domains are alive or dead. Perfect for reconnaissance, monitoring, and security testing.

# Features
Fast Concurrent Processing: Uses asynchronous I/O and multi-threading to efficiently check multiple targets simultaneously
Flexible Targeting: Check a single target or scan multiple hosts from a file
Protocol Handling: Automatically tests both HTTP and HTTPS endpoints
Custom Request Methods: Support for GET, POST, PUT, PATCH, DELETE, OPTIONS, and HEAD requests
Output Organization: Save results to separate files for live and dead servers
Randomized User Agents: Rotates through common user agents to avoid detection
Color-Coded Output: Clear visual distinction between successful and failed probes

#Arguments
target: Single IP or domain to check
-f, --file: File containing list of IPs/domains to check
-m, --method: HTTP request method (default: GET)
-l, --live: File to save accessible domains
-d, --dead: File to save inaccessible domains
-t, --threads: Number of concurrent threads (default: 10)
