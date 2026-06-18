import mysql from 'mysql2/promise'; 

// Membuat connection pool untuk efisiensi kueri database 
export const db = mysql.createPool({ 
  host: process.env.DB_HOST, 
  user: process.env.DB_USER, 
  password: process.env.DB_PASSWORD, 
  database: process.env.DB_NAME, 
  waitForConnections: true, 
  connectionLimit: 10, 
  queueLimit: 0 
}); 