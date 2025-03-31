## LASER Webpage Generator

This Python script reads a CSV file containing curriculum-aligned questions and automatically generates styled HTML quiz pages with hints and answer validation.

Each question is rendered as its own standalone HTML file with:

- 📄 The **question text**
- 📝 An **input field** and **Submit** button
- 💡 A **Hint** button that cycles through multiple hints (if available)
- ✅ Feedback displaying **"Correct!"** or **"Try again."**
- 🔗 A **"Next" button** that links to the next question
- 🔚 At the end of each problem set, a special **Z-END page** is generated showing a unique 7-character code

Each HTML filename includes a random 4-character code (e.g., `H7FX`) to make URLs unpredictable and discourage students from skipping ahead by manually altering links.

---

### 📄 CSV Format and Template Example

https://github.com/user-attachments/assets/0a8c5e32-2f50-4280-8ead-db657781dfee

The generator processes a CSV file with the following column headers:

**Curriculum | Problem Set | Question | Answer | Hint**

Rows with blank cells inherit values from above. This format allows you to list multiple answers and hints for the same question while keeping the file compact.

Here’s a sample structure:

| Curriculum | Problem Set | Question | Answer    | Hint         |
|------------|-------------|----------|-----------|--------------|
| C1         | PS1         | PS1Q1    | PS1Q1A1   | PS1Q1A1H1    |
|            |             |          | PS1Q1A2   | PS1Q1A1H2    |
|            |             |          | PS1Q1A3   | PS1Q1A1H3    |
|            |             |          |           | PS1Q1A1H4    |
|            |             |          |           | PS1Q1A1H5    |
|            |             |          |           | PS1Q1A1H6    |
|            |             |          |           | PS1Q1A1H7    |
|            |             | PS1Q2    | PS1Q2A1   | PS1Q2A1H1    |
|            |             |          | PS1Q2A2   |              |
|            |             |          | PS1Q2A3   |              |
|            | PS2         | PS2Q1    | PS2Q1A1   | PS2Q1A1H1    |
|            |             |          | PS2Q1A2   | PS2Q1A2H1    |
|            |             | PS2Q2    | PS2Q2A1   | PS2Q2A1H1    |
|            |             |          |           | PS2Q2A1H2    |
|            |             |          |           | PS2Q2A1H3    |
|            |             |          |           | PS2Q2A1H4    |
| C2         | PS1         | PS1Q1    | PS1Q1A1   | PS1Q1A1H1    |
|            |             |          | PS1Q1A2   | PS1Q1A2H1    |
|            |             |          |           | PS1Q1A2H2    |
|            |             |          |           | PS1Q1A2H3    |
|            |             | PS1Q2    | PS1Q2A1   | PS1Q2A1H1    |
|            |             |          | PS1Q2A2   |              |

To help you visualize:

- **Curriculum 1 (C1)** has two problem sets: **PS1** and **PS2**, each with **2 questions** (PS1Q1 and PS1Q2 for PS1; PS2Q1 and PS2Q2 for PS2).
- **PS1Q1** in **C1** has **3 answers** and **7 hints**.
- **PS2Q2** has only **1 answer** but **4 hints**.
- **Curriculum 2 (C2)** also has one problem set (**PS1**) with two questions.

The table shown above can be accessed as a [template CSV file](https://docs.google.com/spreadsheets/d/1-jAeX41wwWk84jq3nUdJ-QqRgNa3PpmFB82DFKCLSW8/edit?gid=1006690817#gid=1006690817) and the video above shows a few of the generated webpages using the template data:

---

### ▶️ Running the Generator

https://github.com/user-attachments/assets/dac7f9fe-2656-4ec0-84fc-e9bbe2cd48dc

1. **Install pandas** (if not installed yet):

   ```bash
   pip install pandas
   ```

2. **Place your CSV** in the same folder as the script or modify the path in the script (Line 536):

   ```python
   csv_file = "KT-Questions-S.csv"
   ```

3. **Run the script** via terminal or command line:

   ```bash
   python your_script_name.py
   ```

4. **Output** will be saved in a folder named:

   ```
   LASER-generated-webpages/
   ```

---

### 📁 Sample Input & Output

https://github.com/user-attachments/assets/36682b84-8edf-49ce-bc7f-84aad5e4a00d

To demonstrate the tool's utility when applied to real data, here’s a sample dataset and its corresponding output:

📂 **Google Drive Folder**:  
[KT-Questions-S.csv + Generated Webpages](https://drive.google.com/drive/folders/1y0pkMdfG3p3q-kv5I-L-7k0gxdk79KhR?usp=drive_link)

This folder contains:

- A sample `.csv` file from Dr. Ryan Baker’s ASSISTments course, formatted for the generator
- The resulting HTML quiz pages generated using this tool
- A short video demo showing a user interacting with the generated pages for reference

---

### 💡 Notes

- Make sure your CSV doesn’t contain broken symbols or unsupported characters.
- Comma-separated answers are allowed. The script accepts any answer that matches (case-insensitive).
- The filename structure is randomized but follows the format:

  ```
  C[CUR]-PS[SET]-PS[SET]Q[NUM]-[RANDOM].html
  ```
