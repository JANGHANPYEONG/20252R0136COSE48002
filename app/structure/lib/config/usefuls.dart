//
//
// useful tools.
//
//

import 'package:intl/intl.dart';

class Usefuls {
  /// 현재 날짜를 불러오는 함수
  ///
  /// yyyy-MM-ddThh:mm:ss
  static String getCurrentDate() {
    DateTime now = DateTime.now();
    return DateFormat('yyyy-MM-ddThh:mm:ss').format(now);
  }

  /// 백엔드에서 전송하는 날짜 string을 DateTime 형식으로 변환하는 함수
  ///
  /// yyyy-MM-ddThh:mm:ss 형식으로 입력
  static DateTime dateStringToDateTime(String dateString) {
    DateFormat format = DateFormat("yyyy-MM-ddThh:mm:ss");
    return format.parse(dateString);
  }

  /// 입력 받은 DateTime 변수를 형식에 맞춰 String으로 변환하는 함수
  ///
  /// yyyy-MM-ddThh:mm:ss
  static String dateTimeToDateString(DateTime dateTime) {
    return DateFormat("yyyy-MM-ddThh:mm:ss").format(dateTime);
  }

  /// yyyy-MM-dd 형식의 날짜를 yyyy.MM.ddThh:mm:ss로 변환
  static String dateShortToDateLong(String dateString) {
    DateFormat format = DateFormat("yyyy.MM.dd");
    final temp = format.parse(dateString);
    return dateTimeToDateString(temp);
  }

  /// 육류 도축 날짜 yyyyMMdd 형식을 yyyy.MM.dd 형식으로 변환하는 함수
  static String butcheryDateToDateShort(String butcheryDate) {
    String year = butcheryDate.substring(0, 4);
    String month = butcheryDate.substring(4, 6);
    String day = butcheryDate.substring(6, 8);

    return '$year.$month.$day';
  }

  /// date 형식을 yyyy.MM.dd -> yyyyMMdd로 변환하는 함수
  static String dotDateToDate(String dotDate) {
    String year = dotDate.substring(0, 4);
    String month = dotDate.substring(5, 7);
    String day = dotDate.substring(8, 10);
    return '$year$month$day';
  }

  /// yyyy-MM-ddThh:mm:ss 형식의 날짜를 yyyy.MM.dd 형식으로 파싱
  static String parseDate(String? inputDate) {
    if (inputDate == null) return '-';
    DateTime dateTime = dateStringToDateTime(inputDate);

    // 형식 변환
    String formattedDate =
        "${dateTime.year}.${dateTime.month.toString().padLeft(2, '0')}.${dateTime.day.toString().padLeft(2, '0')}";

    return formattedDate;
  }

  /// 시간 차이 계산
  static int calculateDateDifference(String targetDate) {
    // 현재 로컬 시간 구하기
    DateTime now = DateTime.now();
    // 계산 할 시간 구하기
    DateTime targetDateTime = dateStringToDateTime(targetDate);

    // 두 날짜의 차이 계산
    Duration difference = now.difference(targetDateTime);

    // 일(day) 단위로 반환
    return difference.inDays;
  }
}
