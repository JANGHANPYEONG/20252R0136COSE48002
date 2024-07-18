//
//
// useful tools.
//
//

import 'package:intl/intl.dart';
import 'package:structure/model/meat_model.dart';

class Usefuls {
  /// 현재 날짜
  // TODO : 삭제
  static String getCurrentDate() {
    DateTime now = DateTime.now();
    String createdAt = DateFormat('yyyy-MM-ddTHH:mm:ssZ').format(now);
    return createdAt;
  }

  /// 백엔드에서 전송하는 날짜 string을 DateTime 형식으로 변환하는 함수
  static DateTime dateStringToDateTime(String dateString) {
    DateFormat format = DateFormat("yyyy-MM-dd hh:mm:ss");
    return format.parse(dateString);
  }

  /// period 계산하는 함수
  /// 현재 날짜 - 도축 날짜
  static int getMeatPeriod(MeatModel meatModel) {
    if (meatModel.butcheryYmd == null) return 0;
    DateTime butcheryDate = DateTime.parse(meatModel.butcheryYmd!);
    DateTime currentDate = DateTime.now();

    Duration difference = currentDate.difference(butcheryDate);
    int period = difference.inHours;
    if (period < 0) {
      return 0;
    }
    return period;
  }

  /// 시간 차이 계산
  static int calculateDateDifference(String targetDate) {
    // 현재 로컬 시간 구하기
    DateTime now = DateTime.now();
    // createdAt 시간 구하기
    DateTime targetDateTime = dateStringToDateTime(targetDate);

    // 두 날짜의 차이 계산
    Duration difference = now.difference(targetDateTime);

    // 일(day) 단위로 반환
    return difference.inDays;
  }

  /// yyyy.MM.dd 형식으로 날짜 파싱
  static String parseDate(String? inputDate) {
    if (inputDate == null) return '-';
    DateTime dateTime = dateStringToDateTime(inputDate);

    // 형식 변환
    String formattedDate =
        "${dateTime.year}.${dateTime.month.toString().padLeft(2, '0')}.${dateTime.day}";

    return formattedDate;
  }
}
