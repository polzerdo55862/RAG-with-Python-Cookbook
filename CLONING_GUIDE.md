# Cloning and Copying This Repository

This guide provides step-by-step instructions for cloning this repository and creating your own copy with a similar name.

## Table of Contents
- [Option 1: Fork the Repository on GitHub](#option-1-fork-the-repository-on-github)
- [Option 2: Clone and Create a New Repository](#option-2-clone-and-create-a-new-repository)
- [Option 3: Create a Local Copy with a Different Name](#option-3-create-a-local-copy-with-a-different-name)
- [Post-Setup Steps](#post-setup-steps)

---

## Option 1: Fork the Repository on GitHub

**Best for:** Contributing back to the original project or keeping your copy linked to the original.

### Steps:

1. **Navigate to the repository on GitHub:**
   - Go to: https://github.com/polzerdo55862/RAG-with-Python-Cookbook

2. **Click the "Fork" button** in the top-right corner of the page.

3. **Choose a destination:**
   - Select your GitHub account or organization
   - Optionally, change the repository name (e.g., `My-RAG-with-Python-Cookbook`)
   - Optionally, modify the description
   - Click "Create fork"

4. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

5. **Set up the original repository as an upstream remote** (optional, for syncing updates):
   ```bash
   git remote add upstream https://github.com/polzerdo55862/RAG-with-Python-Cookbook.git
   git fetch upstream
   ```

---

## Option 2: Clone and Create a New Repository

**Best for:** Creating a completely independent copy that's not linked to the original.

### Steps:

1. **Clone the repository without its history:**
   ```bash
   git clone --depth 1 https://github.com/polzerdo55862/RAG-with-Python-Cookbook.git My-RAG-Cookbook
   cd My-RAG-Cookbook
   ```

2. **Remove the original git history:**
   ```bash
   rm -rf .git
   ```

3. **Initialize a new git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Copy of RAG-with-Python-Cookbook"
   ```

4. **Create a new repository on GitHub:**
   - Go to: https://github.com/new
   - Enter a name (e.g., `My-RAG-Python-Cookbook`)
   - Choose public or private
   - **Do NOT** initialize with README, .gitignore, or license
   - Click "Create repository"

5. **Push your code to the new repository:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

---

## Option 3: Create a Local Copy with a Different Name

**Best for:** Working with the repository locally without creating a new GitHub repository.

### Steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/polzerdo55862/RAG-with-Python-Cookbook.git
   ```

2. **Create a copy with a new name:**
   ```bash
   cp -r RAG-with-Python-Cookbook My-RAG-Cookbook
   cd My-RAG-Cookbook
   ```

3. **Update the remote URL** (if you want to push to a different repository):
   ```bash
   git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO_NAME.git
   ```

   Or **remove the remote** if you just want to work locally:
   ```bash
   git remote remove origin
   ```

4. **Optionally, create a fresh git history:**
   ```bash
   rm -rf .git
   git init
   git add .
   git commit -m "Initial commit: Copy of RAG-with-Python-Cookbook"
   ```

---

## Using the Automated Copy Script

For convenience, we provide a bash script that automates Option 3:

```bash
./copy_repo.sh NEW_REPO_NAME
```

For example:
```bash
./copy_repo.sh My-RAG-Cookbook
```

This will create a complete copy of the repository with a new name in the parent directory.

---

## Post-Setup Steps

After creating your copy, consider the following:

### 1. Update Repository Metadata

Edit the `README.md` file to reflect your repository:
- Change the title
- Update GitHub URLs in Colab badges
- Modify the description
- Add your own information

### 2. Update Colab Links

If you want to use Colab with your repository, update all Colab badge URLs in `README.md`:

Replace:
```
https://github.com/polzerdo55862/RAG-with-Python-Cookbook/
```

With:
```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/
```

### 3. Review and Update Dependencies

Check `requirements.txt` files in each chapter directory and ensure all dependencies are up to date:

```bash
# Example: Update dependencies in a chapter
cd ch01_RAG_intro
pip install --upgrade -r requirements.txt
```

### 4. Set Up Your Environment

Follow the setup instructions for individual chapters. Most chapters contain Jupyter notebooks that can be run locally or in Google Colab.

### 5. Customize Content

- Modify examples to fit your use case
- Add your own datasets to the `datasets/` directory
- Extend chapters with your own recipes
- Update images and screenshots

---

## Additional Resources

- **Original Repository:** https://github.com/polzerdo55862/RAG-with-Python-Cookbook
- **GitHub Documentation on Forking:** https://docs.github.com/en/get-started/quickstart/fork-a-repo
- **GitHub Documentation on Cloning:** https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository

---

## License

Please review the original repository's license before creating your copy and ensure you comply with its terms.

---

## Questions or Issues?

If you encounter any problems while cloning or copying this repository, please:
1. Check the [GitHub documentation](https://docs.github.com/)
2. Review this guide carefully
3. Open an issue in your repository for community support
