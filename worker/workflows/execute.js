import executeWorkflow from "./worker.js";
import { Pool } from 'pg';

const pool = new Pool({
    connectionString: "postgresql://postgres:Anusha@localhost:5432/watchdog"
})


async function runWorkflow(workflow_run_id) {

    try {
        await pool.query(
            `UPDATE workflow_runs
             SET status='running', started_at=NOW()
             WHERE id=$1`,
            [workflow_run_id]
        );

        const runResult = await pool.query(
            `SELECT trigger_payload FROM workflow_runs WHERE id=$1`,
            [workflow_run_id]
        );

        const triggerPayload = runResult.rows[0]?.trigger_payload;

        const actions = await pool.query(
            `SELECT ae.id, a.type, a.config
             FROM action_executions ae
             JOIN actions a ON ae.action_id=a.id
             WHERE ae.workflow_run_id=$1
             ORDER BY a."order"`,
            [workflow_run_id]
        );

        for (let action of actions.rows) {

            await pool.query(
                `UPDATE action_executions
                 SET status='running', started_at=NOW()
                 WHERE id=$1`,
                [action.id]
            );

            try {

                const output = await executeWorkflow(action, triggerPayload);

                await pool.query(
                    `UPDATE action_executions
                     SET status='success',
                         output=$2,
                         completed_at=NOW()
                     WHERE id=$1`,
                    [action.id, output]
                );

            } catch (err) {

                await pool.query(
                    `UPDATE action_executions
                     SET status='failed',
                         error_message=$2,
                         completed_at=NOW()
                     WHERE id=$1`,
                    [action.id, err.message]
                );

                await pool.query(
                    `UPDATE workflow_runs
                     SET status='failed',
                         completed_at=NOW()
                     WHERE id=$1`,
                    [workflow_run_id]
                );

                return;
            }
        }

        await pool.query(
            `UPDATE workflow_runs
             SET status='success',
                 completed_at=NOW()
             WHERE id=$1`,
            [workflow_run_id]
        );

    } catch (err) {

        console.log("Worker crash:", err);

        await pool.query(
            `UPDATE workflow_runs
             SET status='failed',
                 completed_at=NOW()
             WHERE id=$1`,
            [workflow_run_id]
        );
    }
}

export default runWorkflow;