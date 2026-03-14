import nodemailer from "nodemailer";

const sendEmail = async (config) => {

    console.log("Send email function called with config:", config, process.env.EMAIL_USER);

    const transporter = nodemailer.createTransport({
        service: "gmail",
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASS
        }
    });

    try {
        await transporter.sendMail({
            from: process.env.EMAIL_USER,
            to: config.to,
            subject: config.subject,
            text: config.body
        });
        console.log("Sent email")
    } catch (err) {
        console.log(err, "error");
        return { message: "Email not sent." }
    }
    return { message: "Email sent successfully" };
};

export default sendEmail;