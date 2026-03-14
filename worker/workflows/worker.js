import sendEmail from "../services/sendEmail.js";

const executeWorkflow = async (action) => {

    switch (action.type) {
        case 'email':
            await sendEmail(action.config);
            return { message: "Email sent!"}
        case 'manual':
            await new Promise(resolve => setTimeout(resolve, 1000));
            return { message: "Manual action done"}
        default:
            return {message: "Unknown action type"}
    }
}

export default executeWorkflow;