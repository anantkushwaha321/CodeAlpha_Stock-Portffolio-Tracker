# Stock Portfolio Tracker

A beginner-friendly, browser-based Stock Portfolio Tracker built with Python's standard library. It runs locally on your computer and provides a modern responsive dashboard for managing sample stock holdings and calculating total investment value.

> **Educational demo:** all stock prices are hardcoded example values in USD. The application does not retrieve live market prices and is not financial advice.

## Features

- Prominent **Total Investment Value** display that recalculates from every holding.
- Predefined sample stock catalogue: AAPL, TSLA, GOOGL, MSFT, and AMZN.
- Add shares and automatically combine quantities for an existing stock.
- Remove a stock holding or reset the entire portfolio.
- Portfolio metrics for holding count and total shares.
- Responsive dark dashboard with stock cards, holdings table, and portfolio-allocation bars.
- Export the current portfolio and total investment to CSV.
- Input validation and helpful messages for invalid entries.
- No pip installs, external packages, API keys, database, or internet connection required.

## Requirements

- Python 3.9 or newer recommended.
- A modern browser such as Chrome, Edge, or Firefox.
- No third-party Python packages are needed.

## Project files

```text
StockPortfolioTracker/
├── main.py
└── README.md
```

## Run on Windows (VS Code)

1. Put `main.py` and `README.md` in the same folder.
2. Open that folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:

   ```powershell
   python main.py
   ```

   If your system uses the Python launcher instead, run `py main.py`.

5. The default browser should open automatically at:

   **http://127.0.0.1:8765**

6. Keep the terminal window running while using the dashboard. To stop the server, return to the terminal and press **Ctrl+C**.

## Why the total shows correctly

The browser requests portfolio data from the Python endpoint `/api/portfolio`. The backend recalculates each holding as:

```text
Investment Value = Predefined Share Price × Quantity
Total Investment = Sum of all holding values
```

For example, the initial demo portfolio contains:

| Symbol | Example price | Quantity | Investment value |
|---|---:|---:|---:|
| AAPL | $180.00 | 5 | $900.00 |
| TSLA | $250.00 | 2 | $500.00 |
| **Total** | | **7 shares** | **$1,400.00** |

The dashboard displays the total in the large summary area and the three metric cards. It fetches refreshed data after adding, removing, or resetting holdings. The server calculates totals from stock symbols and quantities instead of trusting any previously stored total field.

## How to use the dashboard

1. Click a stock catalogue card or select a stock from the dropdown.
2. Enter a positive whole-number share quantity.
3. Review the estimated holding value.
4. Click **Add to portfolio**. If the stock already exists, the new shares are added to its quantity.
5. Review the updated total investment and allocation bars.
6. Use **Remove** to remove one holding, **Reset** to clear all holdings, or **Export CSV** to download a report.

The reset action asks for confirmation. The app starts with two sample holdings so the total value is visible on first launch; resetting clears them. Portfolio data is held in memory while the server runs, so it resets when the Python process is restarted. Export the CSV if you want to keep a report.

## Troubleshooting

### The page will not open
- Make sure the terminal still shows that the server is running.
- Try opening `http://127.0.0.1:8765` manually.
- If port `8765` is already in use, close the other process or change `PORT = 8765` near the top of `main.py` to another unused port, then restart.

### The total shows “Unavailable”
- Check that the Python terminal is still running.
- Refresh the browser page.
- Check the browser Developer Tools Console/Network tab for a failed `/api/portfolio` request.
- Stop the server with Ctrl+C and restart it using `python main.py`.

### Python command is not recognized
Install Python from the official Python website and enable **Add Python to PATH** during installation, then reopen VS Code. Alternatively, try `py main.py`.

## Main Python concepts demonstrated

- **Dictionary:** maps stock symbols to predefined prices and company names.
- **List:** stores the user's current portfolio holdings.
- **Functions:** keeps investment calculation and response building reusable.
- **Loops and conditionals:** updates existing holdings, validates user input, and builds portfolio summaries.
- **Arithmetic:** multiplies price by quantity and adds individual holding values.
- **HTTP server and JSON:** Python serves the HTML dashboard and provides portfolio data to the browser using its built-in `http.server` module.
- **CSV export:** the browser exports a spreadsheet-friendly CSV report.

## Limitations

- The stock catalogue and prices are fixed sample data.
- Portfolio changes exist in memory only until the server stops; use CSV export to save a report.
- This is a local educational project, not a production investment platform.
