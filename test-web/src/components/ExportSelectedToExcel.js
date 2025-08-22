import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const ExportSelectedToExcel = (selectedIds, allData) => {
  const selectedData = allData.filter(row => selectedIds.includes(row.id));

  // 정제: 필요한 필드만 추출
  const exportData = selectedData.map(row => ({
    ID: row.id,
    날짜: row.date,
    파장: row.wavelength,
    ...row.prediction, // 예측값
    ...Object.fromEntries( // 관능평가 값 붙이기 (prefix 붙여 구분)
      Object.entries(row.sensory || {}).map(([k, v]) => [`관능평가_${k}`, v])
    ),
  }));

  const worksheet = XLSX.utils.json_to_sheet(exportData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, '예측결과');

  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });

  saveAs(blob, 'prediction_result.xlsx');
};

export default ExportSelectedToExcel;