// fetch한 JSON 데이터에서 필요한 값 parsing 및 전처리하여 series에 저장
// 결합된 카테고리
const combinedCategories = ['안심', '등심', '목심', '앞다리', '갈비'];
const cattleCategories = ['채끝', '우둔', '설도', '양지', '사태'];
const porkCategories = ['삼겹살', '뒷다리'];

const processStackedBarData = (data, setSeries) => {
  if (
    !data['beef_counts_by_primal_value'] ||
    !data['pork_counts_by_primal_value']
  ) {
    console.error('올바르지 않은 데이터 형식:', data);
    return;
  }
  // parsing
  const cattleData = data['beef_counts_by_primal_value'];
  const porkData = data['pork_counts_by_primal_value'];

  // [{name:'부위 별 이름', data : '부위 별 개수'}, ... ] 형태로 데이터 전처리
  let seriesArr = [];

  const allCategories = [
    ...combinedCategories,
    ...cattleCategories,
    ...porkCategories,
  ];
  allCategories.map((c) => {
    seriesArr = [
      ...seriesArr,
      {
        name: c,
        data: [
          cattleData[c] !== undefined ? cattleData[c] : 0,
          porkData[c] !== undefined ? porkData[c] : 0,
        ],
      },
    ];
  });

  // series에 저장
  setSeries(seriesArr);
};

export default processStackedBarData;
