[![Docker Image CI](https://github.com/paeljojy/StockBrokerage/actions/workflows/docker-image.yml/badge.svg)](https://github.com/paeljojy/StockBrokerage/actions/workflows/docker-image.yml)
[![build](https://github.com/paeljojy/StockBrokerage/actions/workflows/main.yml/badge.svg)](https://github.com/paeljojy/StockBrokerage/actions/workflows/main.yml)

# Apple Stock Brokerage Application
Read docs/* for more information

# Dependencies
## Frontend
vuejs
## Backend
expressjs

# Building

## Frontend
```bash
npm install
npm run build

# Run for development
npm run dev 

## Backend
npm install
cd Server
tsc && node dist/Server.js


```

# Scripts provided
Install dependencies and build the project for the first time.
```bash
# Linux / Mac / WSL
./Scripts/init.sh
```

```batch
@REM Windows
Scripts/init.bat 
```

