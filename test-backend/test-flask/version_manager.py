# 타임스탬프 버전 관리 방식 (옵션)
def get_versioned_filename(base_path, filename):
    """
    파일이 이미 존재하면 타임스탬프를 추가한 새로운 파일명 생성
    예: 140119100857.csv -> 140119100857_20250812_112345.csv
    """
    if not os.path.exists(os.path.join(base_path, filename)):
        return filename
    
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_filename = f"{name}_{timestamp}{ext}"
    
    return versioned_filename

# 사용 예시:
# csv_filename = get_versioned_filename(csv_dir, csv_filename)
# zip_filename = get_versioned_filename(image_dir, zip_filename)
