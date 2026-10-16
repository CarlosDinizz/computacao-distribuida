const express = require('express');
const app = express();
const PORT = 3000;

const FLASK_URL = "http://localhost:5000";

app.use(express.json());

app.get('/', (req, res) => {
    try {
        console.log(`200 GET '/' | ${new Date().toISOString()}`);
        return res.status(200).json("Hello World!");
    } catch (err) {
        console.log(`500 GET '/' | ${new Date().toISOString()}`);
        return res.status(500).json({"message": "Ocorreu um erro no servidor", "status": 500, "error": err});
    }
})

app.listen(PORT, () => {
    console.log(`Servidor Node rodando na porta ${PORT}`);
});