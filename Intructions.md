# Step-by-Step Guide: How to Fork, Clone, and Contribute

Follow these instructions to participate in the test.

### 1. **Fork the Repository**
1. Go to the repository URL (provided by your instructor).
2. In the top-right corner of the page, click the **Fork** button.
3. This will create a copy of the repository in your GitHub account.

### 2. **Clone Your Fork**
1. After forking, go to your GitHub account and open your **forked repository**.
2. Click on the green **Code** button and copy the URL.
3. Open your terminal and run the following command to clone your fork:
   ```bash
   git clone https://github.com/your-username/your-repository.git
   ```
4. Navigate into the cloned directory:
   ```bash
   cd your-repository
   ```

### 3. **Create a New Branch**
1. Before making changes, create a **new branch** for your work. You can name it like `user-<your-username>-test`:
   ```bash
   git checkout -b user-<your-username>-test
   ```

### 4. **Make Changes**
1. Edit files in the repository as required by the test.
2. After completing your changes, save the files.

### 5. **Commit and Push Changes**
1. Stage your changes:
   ```bash
   git add .
   ```
2. Commit your changes:
   ```bash
   git commit -m "Completed the test task"
   ```
3. Push your changes to your fork:
   ```bash
   git push origin user-<your-username>-test
   ```

### 6. **Create a Pull Request (PR)**
1. Go to the **original repository** where you forked from.
2. You will see an option to **Create Pull Request** for the branch you just pushed.
3. Click **New Pull Request**.
4. Ensure the **base branch** is `main` and the **compare branch** is your own branch (`user-<your-username>-test`).
5. Add a description if needed, then click **Create Pull Request**.

---

### **Important Notes**
- **No need to merge with `main`**: You **do not** need to merge with the `main` branch in your fork.
- **Always work on your own branch**: Do not push directly to `main`. Always create and work on a separate branch.
- **Submit a pull request to the original repository**: After pushing to your own branch, open a pull request to merge your changes into `main` in the original repository.
