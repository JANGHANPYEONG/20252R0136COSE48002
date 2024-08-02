//두 배열의 상관관계 계산
const calculateCorrelation = (arr1, arr2) => {
    if (arr1.length !== arr2.length) {
      return 0;
    }

    const n = arr1.length;

    const sum1 = arr1.reduce((acc, value) => acc + value, 0);
    const sum2 = arr2.reduce((acc, value) => acc + value, 0);

    const sum1Squared = arr1.reduce((acc, value) => acc + value * value, 0);
    const sum2Squared = arr2.reduce((acc, value) => acc + value * value, 0);

    const productSum = arr1
      .map((value, index) => value * arr2[index])
      .reduce((acc, value) => acc + value, 0);

    const numerator = n * productSum - sum1 * sum2;
    const denominator = Math.sqrt(
      (n * sum1Squared - sum1 ** 2) * (n * sum2Squared - sum2 ** 2)
    );

    if (denominator === 0) {
      return 0;
    }

    const correlation = (numerator / denominator) * 100;
    return parseFloat(correlation.toFixed(3)); // 소수점 세 번째 자리까지 반올림
  }
export default calculateCorrelation