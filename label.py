import pandas as pd

def match_labels():
    """
    Đọc dữ liệu từ label.csv và main_posts.csv, 
    match theo index đã điều chỉnh và tạo cột label mới
    """
    
    # Đọc dữ liệu từ các file CSV
    try:
        label_df = pd.read_csv('data/label.csv')
        main_df = pd.read_csv('data/main_posts.csv')
        
        print(f"Đã đọc label.csv: {len(label_df)} dòng")
        print(f"Đã đọc main_posts.csv: {len(main_df)} dòng")
        
    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file - {e}")
        return
    
    # Lọc chỉ lấy những dòng có final_label = 1
    filtered_label_df = label_df[label_df['final_label'] == 1]
    print(f"Số dòng có final_label = 1: {len(filtered_label_df)}")
    
    # Tạo dictionary để map từ index thật sang label
    # index_get trong label.csv = index thật + 1
    # Nên index thật = index_get - 1
    label_mapping = {}
    
    for _, row in filtered_label_df.iterrows():
        real_index = row['index_get']   # Điều chỉnh index lệch 1
        label_mapping[real_index] = 1  # Nếu có trong label.csv và final_label = 1 thì label = 1
    
    print(f"Tạo mapping cho {len(label_mapping)} index có final_label = 1")
    print(f"Các index được label (final_label = 1): {sorted(label_mapping.keys())}")
    
    # Tạo cột label cho main_posts.csv
    # Reset index để đảm bảo index bắt đầu từ 0
    main_df = main_df.reset_index(drop=True)
    
    # Tạo cột label: 1 nếu index có trong mapping (final_label = 1), 0 nếu không
    main_df['label'] = main_df.index.map(label_mapping).fillna(0).astype(int)
    
    # Thống kê kết quả
    label_1_count = (main_df['label'] == 1).sum()
    label_0_count = (main_df['label'] == 0).sum()
    
    print(f"\nKết quả:")
    print(f"- Số dòng có label = 1 (final_label = 1): {label_1_count}")
    print(f"- Số dòng có label = 0: {label_0_count}")
    print(f"- Tổng số dòng: {len(main_df)}")
    
    # Lưu file mới
    output_file = 'main_posts_with_labels.csv'
    main_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nĐã lưu kết quả vào file: {output_file}")
    
    # Hiển thị một vài dòng mẫu để kiểm tra
    print(f"\nMột vài dòng mẫu có label = 1 (từ final_label = 1):")
    sample_labeled = main_df[main_df['label'] == 1].head(3)
    for idx, row in sample_labeled.iterrows():
        print(f"Index {idx}: {row['text'][:100]}...")
    
    return main_df

# Chạy hàm
if __name__ == "__main__":
    result_df = match_labels()