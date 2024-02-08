import express from 'express';
import mariadb from 'mariadb';
import sqlite3 from 'sqlite3';
import { getStocks } from './Stocks.ts';

const app = express()
const port = 3000;

var router = express.Router()

router.get('/seppo', function(req, res, next) {
    console.log("Seppppppppppppppppppppppppo");
});

async function getDB() {
    // MariaDB version
    /* const pool = mariadb.createPool({ host: process.env.DB_HOST, user: process.env.DB_USER, connectionLimit: 5 }); */
    const pool = mariadb.createPool({
        host: 'localhost',
        user: 'root',
        password: '',
        connectionLimit: 5,
        port: 3306,
        database: 'stock_brokerage'
    });

    let conn;
    try {
        conn = await pool.getConnection();
        const rows = await conn.query("SELECT * from users");

        console.log(rows);
        return rows;
        /* const res = await conn.query("INSERT INTO myTable value (?, ?)", [1, "mariadb"]); */
        // res: { affectedRows: 1, insertId: 1, warningStatus: 0 }
    }
    finally {
        if (conn) {
            conn.release(); //release to pool
        }
    }
}

app.get('/', (req, res) => {
    /* const db = getDB(); */
    /* res.send('SENT DATA HERE!'); */
    /* res.send(db.toString()); */
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});

app.get('/api/stocks/apple', async (req, res) => {

});

app.get('/api/data', async (req, res) => {
    const db = new sqlite3.Database('Database/Main.db');
    db.get("SELECT * FROM users;",
        (err, data) => {
            console.log("Got query data.");
            /* console.log(data); */
            res.json(data);
        });
    db.close();
});

