// 서버 없이 클라이언트에서 파일 다운로드하는 방식
export const downloadFiles = (data, columns, zipFile) => {
  try {
    // 이력번호 추출
    const managementNumber = data.length > 0 ? data[0]['이력번호'] : 'unknown';
    
    // "매핑 상태" 컬럼 제외하고 CSV 생성
    const filteredColumns = columns.filter(col => col !== '매핑 상태');
    const csvHeader = filteredColumns.join(',') + '\n';
    const csvRows = data.map(row => 
      filteredColumns.map(col => {
        const value = row[col] ?? '';
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    const csvContent = csvHeader + csvRows.join('\n');

    // CSV 파일 다운로드
    const csvBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const csvUrl = URL.createObjectURL(csvBlob);
    const csvLink = document.createElement('a');
    csvLink.href = csvUrl;
    csvLink.download = `${managementNumber}.csv`;
    csvLink.click();
    URL.revokeObjectURL(csvUrl);

    // ZIP 파일 다운로드 (이미 있는 파일이므로 그대로)
    const zipUrl = URL.createObjectURL(zipFile);
    const zipLink = document.createElement('a');
    zipLink.href = zipUrl;
    zipLink.download = zipFile.name;
    zipLink.click();
    URL.revokeObjectURL(zipUrl);

    return {
      success: true,
      message: `파일이 다운로드되었습니다.\n- CSV: ${managementNumber}.csv\n- ZIP: ${zipFile.name}`,
      data: {
        csvFileName: `${managementNumber}.csv`,
        zipFileName: zipFile.name,
        dataCount: data.length
      }
    };

  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: `다운로드 실패: ${error.message}`
    };
  }
};

export default downloadFiles;
