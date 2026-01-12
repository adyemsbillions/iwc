# IWC Exchange Backend 🚀

Backend API for **IWC Exchange**, a digital exchange platform built with **FastAPI**.  
This project handles authentication, user profiles, dashboards, and future financial operations.

---

## 📌 Project Status

🛠 **Active Development**

---

## 🧩 Tech Stack

- **Python**
- **FastAPI**
- **MySQL**
- **PyMySQL**
- **JWT Authentication**
- **Passlib (bcrypt)**
- **Uvicorn**

---

## 📂 Project Structure

## here i added the alteration code for users

ALTER TABLE users
ADD COLUMN is_verified TINYINT DEFAULT 0,
ADD COLUMN verification_token VARCHAR(255);

also please nehemiah check the signup and update to check isverify if set to 1 then should grand login else echo user should check email and verify.
