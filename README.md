## 📄 How to Use the LASER Webpage Generator

This Python script reads a CSV file containing curriculum-aligned questions and automatically generates styled HTML quiz pages with hints and answer validation.

### 🗂 CSV Format

Your CSV file (e.g., `KT-Questions-S.csv`) should include the following columns:

| Curriculum | Problem Set | Question       | Answer | Hint                    |
|------------|-------------|----------------|--------|-------------------------|
| Algebra    | Set 1       | What is 2 + 2? | 4      | Try using your fingers! |
|            |             |                | Four   | It's the same as 2 doubled. |
|            |             |                |        | Think of pairs.         |

- A new question starts when the `Question` column is filled.
- Additional `Answer` and `Hint` rows can follow.
- The script assumes UTF-8 encoding. Convert special characters like `≥` to `>=` before running.

---

### 🎥 Template Example

Please explore this template example to see how the generator handles a CSV with multiple Curriculums, Problem Sets, Questions, Answers, and Hints — and what the corresponding generated webpages look like:

<video width="700" controls>
  <source src="https://neithan.rocks/LASERWebpageGeneratorExample.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---

### ▶️ Running the Generator

1. **Place your CSV** in the same folder as the script or modify the path in the script:

   ```python
   csv_file = "KT-Questions-S.csv"
   ```

2. **Run the script** via terminal or command line:

   ```bash
   python your_script_name.py
   ```

3. **Output** will be saved in a folder named:

   ```
   LASER-generated-webpages/
   ```

Each question gets its own HTML file with:
- Question text
- Input field and Submit button
- Hint button (cycles through multiple hints)
- Feedback ("Correct" or "Try again")
- "Next" button linking to the next question

At the end of each set, a **Z-END** page with a unique code is generated.

---

### 💡 Notes

- Make sure your CSV doesn’t contain broken symbols or unsupported characters.
- Comma-separated answers are allowed. The script accepts any answer that matches (case-insensitive).
- The filename structure is randomized but follows the format:

  ```
  C[CUR]-PS[SET]-PS[SET]Q[NUM]-[RANDOM].html
  ```
