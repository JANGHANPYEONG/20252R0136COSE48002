import { apiIP } from '../config';

export const uploadMeatData = async (csvRows, columns, zipFile) => {
  // 1. CSV 문자열 생성
  const csvHeader = columns.join(',') + '\n';
  const csvRowsStr = csvRows.map((row) =>
    columns.map((col) => row[col] ?? '').join(',')
  );
  const csvContent = csvHeader + csvRowsStr.join('\n');

  // 2. FormData 구성
  const formData = new FormData();
  formData.append('csv', new Blob([csvContent], { type: 'text/csv' }), 'metadata.csv');
  formData.append('zipfile', zipFile);

  // 3. API 호출
  const res = await fetch(`http://${apiIP}/meat/batch-upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`업로드 실패: ${errText}`);
  }

  return await res.json();
};
