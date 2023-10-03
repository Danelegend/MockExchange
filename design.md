Exchange Architecture

Accumulator -> Risk Management System -> Matching Engine -> Primary Data Server -> Broadcast Server

 - Accumulator: Accept incoming requests
 - RMS: Ensure requests meet predefined parameters
 - Matching Engine: Match requests to orders, store orders
 - Primary Data Server: Turn trades into ticks (1s)
 - Broadcast Server: Distribute outgoing ticks and matches