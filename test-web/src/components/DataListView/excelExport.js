import * as XLSX from 'xlsx';
import { apiIP } from '../../config';

// export 할 육류 데이터 목록 fetch
const getDataListJSON = async () => {
  try {
    const response = await fetch(`http://${apiIP}/meat/get`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const json = await response.json();
    return json;
  } catch (error) {
    console.error('Fetch error:', error);
    return null; // 또는 빈 객체나 배열을 반환할 수 있습니다.
  }
};

// JSON 데이터를 엑셀로 변환하기
const downloadExcel = (data) => {
  const rows = DataListJSON2Excel(data);
  const worksheet = XLSX.utils.json_to_sheet(rows);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'my_sheet');
  XLSX.writeFile(workbook, '데이터목록.xlsx');
};

// json 데이터 가공
const DataListJSON2Excel = (rawData) => {
  let newData = [];

  // id_list에 있는 ID들을 사용하여 meat_dict에서 데이터를 가져옴
  rawData.id_list.forEach((id) => {
    const meatData = rawData.meat_dict[id];
    if (meatData) {
      newData.push(meatData);
    }
  });

  return newData;
};

export { getDataListJSON, downloadExcel };
