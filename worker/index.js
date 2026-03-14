import express from 'express'
import dotenv from 'dotenv';
import runWorkflow from './workflows/execute.js';

dotenv.config();

const app = express()
app.use(express.json())


app.post("/execute", async (req, res) => {
    const { workflow_run_id } = req.body;

    res.json({ message: "Execution started" });

    runWorkflow(workflow_run_id); // background execution
})

app.listen(3000, () => {
    console.log("Executor is running on port: 3000")
})
