# Hashiwokakero Solver

## Giới thiệu
**Project 2: Hashiwokakero - Nhóm 11**

23127531 - Chu Quốc Anh Minh

22127124 - Nguyễn Anh Hoàng

22127356 - Trần Nguyễn Lộc Quý 

## Yêu cầu hệ thống
- Python 3.7 trở lên
- Thư viện PySAT (dùng cho thuật toán PySAT)

## Cài đặt
1. **Kiểm tra Python**:
   - Đảm bảo Python 3.7+ đã được cài đặt:
     ```
     python --version
     ```
2. **Cài đặt thư viện**:
   - Cài đặt `pysat` từ file `requirements.txt`:
     ```
     pip install -r requirements.txt
     ```

3. **Chuẩn bị file đầu vào**:
   - Tạo thư mục `Inputs` và đặt file đầu vào (ví dụ: `input-01.txt`) với định dạng như đề yêu cầu (mỗi dòng là một hàng của grid, các số cách nhau bằng dấu phẩy). Ví dụ:
     ```
     0 , 2 , 0 , 5 , 0 , 0 , 2
     0 , 0 , 0 , 0 , 0 , 0 , 0
     4 , 0 , 2 , 0 , 2 , 0 , 4
     0 , 0 , 0 , 0 , 0 , 0 , 0
     0 , 1 , 0 , 5 , 0 , 2 , 0
     0 , 0 , 0 , 0 , 0 , 0 , 0
     4 , 0 , 0 , 0 , 0 , 0 , 3
     ```

## Cách chạy
1. **Chạy chương trình:**
   ```
   python main.py
   ```

2. **Nhập tên file đầu vào**

   Lưu ý: Đảm bảo file đầu vào phải tồn tại trong thư mục `Inputs`

3. **Chọn thuật toán để chạy thông qua các số từ 1-5:**
   1. PySAT
   2. Backtracking
   3. A*
   4. Brute-Force
   5. Tất cả

   Lưu ý: Sử dụng thuật toán PySAT trên grid lớn (9x9 trở lên) và các thuật toán còn lại trên grid nhỏ.

4. **Đầu ra**:
   - In tên file đầu vào và lời giải kèm thời gian cho từng thuật toán trên terminal.
   - Lưu lời giải vào file output-<tên file đầu vào>.txt trong thư mục `Outputs`
   - Lời giải hiển thị với:
     - Số: Độ của đảo.
     - `-` hoặc `=`: Cầu đơn hoặc đôi ngang.
     - `|` hoặc `$`: Cầu đơn hoặc đôi dọc.

## Ví dụ đầu ra
Cho grid:
```
0 , 2 , 0 , 5 , 0 , 0 , 2
0 , 0 , 0 , 0 , 0 , 0 , 0
4 , 0 , 2 , 0 , 2 , 0 , 4
0 , 0 , 0 , 0 , 0 , 0 , 0
0 , 1 , 0 , 5 , 0 , 2 , 0
0 , 0 , 0 , 0 , 0 , 0 , 0
4 , 0 , 0 , 0 , 0 , 0 , 3
```
Kết quả (ví dụ PySAT):
```
map: input-01.txt
--- Giải bằng PySAT ---
Tìm thấy lời giải trong 0.0012 giây.

Lời giải:
[ "0" , "2" , "=" , "5" , "-" , "-" , "2" ]
[ "0" , "0" , "0" , "$" , "0" , "0" , "|" ]
[ "4" , "=" , "2" , "$" , "2" , "=" , "4" ]
[ "$" , "0" , "0" , "$" , "0" , "0" , "|" ]
[ "$" , "1" , "-" , "5" , "=" , "2" , "|" ]
[ "$" , "0" , "0" , "0" , "0" , "0" , "|" ]
[ "4" , "=" , "=" , "=" , "=" , "=" , "3" ]
```

## Lưu ý
- Đảm bảo thư mục `Inputs` tồn tại và chứa file đầu vào hợp lệ.
- Nếu file đầu vào không tồn tại hoặc không hợp lệ, chương trình báo lỗi.
- Sử dụng thuật toán PySAT trên grid lớn (9x9 trở lên) và các thuật toán còn lại trên grid nhỏ.