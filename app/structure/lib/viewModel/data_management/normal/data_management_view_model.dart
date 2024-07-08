import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:structure/components/get_qr.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/main.dart';
import 'package:structure/model/user_model.dart';

class DataManagementHomeViewModel with ChangeNotifier {
  UserModel userModel;
  DataManagementHomeViewModel(this.userModel) {
    _initialize();
  }
  late BuildContext _context;
  // 초기 리스트
  List<Map<String, String>> numList = [];

  // 필터링된 리스트
  List<Map<String, String>> filteredList = [];

  // 선택된 리스트
  List<Map<String, String>> selectedList = [];

  // 검색 필드를 지칭
  String insertedText = '';
  final FocusNode focusNode = FocusNode();
  final TextEditingController controller = TextEditingController();

  bool isLoading = true;
  bool isOpnedFilter = false; // 필터가 열린지 확인.
  bool isOpenTable = false; // 날짜 선택이 열린지 확인.
  bool isChecked = false; // 필터 값이 온전한지 확인 (직접 입력에서 날짜가 정확히 골라졌는지 여부)

  // 필터 값을 지칭
  String filterdResult = '3일∙최신순';

  // 필터에 필요한 변수
  List<String> dateList = ['3일', '1개월', '3개월', '직접입력'];
  List<bool> dateStatus = [true, false, false, false];
  int dateSelectedIdx = 0;

  List<String> sortList = ['최신순', '과거순'];
  List<bool> sortStatus = [true, false];
  int sortSelectedIdx = 0;

  // 날짜 값이 담길 변수
  DateTime? toDay;
  DateTime? threeDaysAgo;
  DateTime? monthsAgo;
  DateTime? threeMonthsAgo;

  // 임시 변수
  DateTime focused = DateTime.now();
  DateTime? temp1;
  DateTime? temp2;
  DateTime? firstDay;
  DateTime? lastDay;
  String firstDayText = '';
  String lastDayText = '';
  int indexDay = 0;

  // 초기화 함수.
  Future<void> _initialize() async {
    await _fetchData();
    filterlize();
    isLoading = false;
    notifyListeners();
  }

  // 필터링 시 호출될 함수
  void filterlize() {
    setTime();
    setDay();
    sortUserData();
  }

  // 직접 설정 필터가 적용된 후, 날짜 선택이 완료 되었는지 판단
  bool checkedFilter() {
    if (dateStatus[3] == true && (temp1 == null || temp2 == null)) {
      return false;
    } else {
      return true;
    }
  }

  // 필터 조회 버튼 클릭시 호출
  void onPressedFilterSave() {
    // 필터 값 기억
    dateSelectedIdx = dateStatus.indexWhere((element) => element == true);
    sortSelectedIdx = sortStatus.indexWhere((element) => element == true);

    // 필터 텍스트 할당
    filterdResult = '${dateList[dateSelectedIdx]}∙${sortList[sortSelectedIdx]}';

    // 필터 창 닫기
    isOpnedFilter = false;
    isOpenTable = false;

    dateSwap();

    // 임시 날짜 값을 실제 날자 값에 할당. (직접 설정)
    firstDay = temp1;
    lastDay = temp2;

    formatting();
    filterlize();
    notifyListeners();
  }

  // 날짜 fomatting
  void formatting() {
    isOpenTable = !isOpenTable;

    if (firstDay != null) {
      firstDayText = DateFormat('yyyy.MM.dd').format(firstDay!);
    }
    if (lastDay != null) {
      lastDayText = DateFormat('yyyy.MM.dd').format(lastDay!);
    }
    notifyListeners();
  }

  // 직접 설정 과정에서 범위를 재 지정함. (범위의 앞 보다 뒤가 더 빠른 날짜 일 때, 둘을 뒤 바꿈.)
  void dateSwap() {
    if (temp1 != null && temp2 != null) {
      bool isA = temp1!.isAfter(temp2!);
      if (isA == true) {
        DateTime dtemp = temp1!;
        temp1 = temp2;
        temp2 = dtemp;
        String ttemp = firstDayText;
        firstDayText = lastDayText;
        lastDayText = ttemp;
      }
    }
  }

  // 필터가 활성화 되면 호출.
  void clickedFilter() {
    // 이전의 필터 값을 받아 필터 초기화.
    dateStatus = List.filled(dateStatus.length, false);
    dateStatus[dateSelectedIdx] = true;
    sortStatus = List.filled(sortStatus.length, false);
    sortStatus[sortSelectedIdx] = true;

    // '직접 설정'이 아니면 날짜 지정 부분을 가린다.
    if (dateSelectedIdx != 3) {
      firstDayText = '';
      lastDayText = '';
    } else {
      formatting();
      // 날짜 변경에 임시 변수 할당. (적용 시에만 필터 값 적용)
      temp1 = firstDay;
      temp2 = lastDay;
    }

    // 날짜 할당이 없을 시에, 임시 변수 초기화.
    if (firstDay == null || lastDay == null) {
      temp1 = null;
      temp2 = null;
    }
    // 필터 on/off 조절
    isOpnedFilter = !isOpnedFilter;
    if (isOpenTable) {
      isOpenTable = false;
    }
    notifyListeners();
  }

  // 날짜 필터를 이용할 때 호출된다.
  void onTapDate(int index) {
    dateStatus = List.filled(dateStatus.length, false);
    dateStatus[index] = true;
    // 직접 설정이면 TableCalendar 호출
    if (index != 3) {
      isOpenTable = false;
      firstDayText = '';
      lastDayText = '';
    } else {
      formatting();
    }

    // 직접 입력이 아닐 경우 임시 변수 초기화.
    if (firstDay == null || lastDay == null) {
      temp1 = null;
      temp2 = null;
    }

    notifyListeners();
  }

  // 정렬 필터링
  void onTapSort(int index) {
    sortStatus = List.filled(sortStatus.length, false);
    sortStatus[index] = true;
    notifyListeners();
  }

  // TableCalendar 관련 함수
  void onTapTable(int index) async {
    // 만일 날짜를 처음 지정할 시 기존 값을 초기화
    if (firstDay == null || lastDay == null) {
      focused = DateTime.now();
    }
    isOpenTable = true;
    indexDay = index;
    // 날짜 지정 이후 선택할 시 이전 날짜 호출
    if (index == 0 && temp1 != null) {
      focused = temp1!;
    } else if (index == 1 && temp2 != null) {
      focused = temp2!;
    }
    dateSwap();
    notifyListeners();
  }

  // TableCalendar 위젯에 사용될 날짜 변경 함수
  void onDaySelected(DateTime selectedDay, DateTime focusedDay) {
    focused = selectedDay;
    // 시작 | 종료 중 어느 지점이 변경될 지 지정
    if (indexDay == 0) {
      temp1 = selectedDay;
      firstDayText = DateFormat('yyyy.MM.dd').format(temp1!);
    } else {
      temp2 = selectedDay;
      lastDayText = DateFormat('yyyy.MM.dd').format(temp2!);
    }
    notifyListeners();
  }

  // 현재 필터링 시간을 기준으로 시간 지정 (현재 날짜에 맞추어, 3일 | 1개월 | 3개월 날짜가 지정된다.)
  // 현재 지정 방식에서는 3일 전이면, 현재 시간을 기준으로 3일 전 자정까지이다.
  void setTime() {
    toDay = DateTime.now();
    threeDaysAgo =
        DateTime(toDay!.year, toDay!.month, toDay!.day - 3, 0, 0, 0, 0);
    monthsAgo = DateTime(toDay!.year, toDay!.month - 1, toDay!.day, 0, 0, 0, 0);
    threeMonthsAgo =
        DateTime(toDay!.year, toDay!.month - 3, toDay!.day, 0, 0, 0, 0);
  }

  // 정렬 방식 입력에 따라 필터링
  void sortUserData() {
    filteredList.sort((a, b) {
      DateTime dateA = DateTime.parse(a["createdAt"]!);
      DateTime dateB = DateTime.parse(b["createdAt"]!);
      if (sortSelectedIdx == 1) {
        return dateA.compareTo(dateB);
      } else {
        return dateB.compareTo(dateA);
      }
    });
    selectedList = filteredList;
  }

  // 날짜 필터 입력에 따라 필터링
  void setDay() {
    filteredList = numList;
    if (dateSelectedIdx == 0) {
      print('3일');
      filteredList = filteredList.where((data) {
        DateTime dateTime = DateTime.parse(data["createdAt"]!);
        return dateTime.isAfter(threeDaysAgo!) && dateTime.isBefore(toDay!);
      }).toList();
    } else if (dateSelectedIdx == 1) {
      print('1개월');
      filteredList = filteredList.where((data) {
        DateTime dateTime = DateTime.parse(data["createdAt"]!);
        return dateTime.isAfter(monthsAgo!) && dateTime.isBefore(toDay!);
      }).toList();
    } else if (dateSelectedIdx == 2) {
      print('3개월');
      filteredList = filteredList.where((data) {
        DateTime dateTime = DateTime.parse(data["createdAt"]!);
        return dateTime.isAfter(threeMonthsAgo!) && dateTime.isBefore(toDay!);
      }).toList();
    } else {
      print('직접설정');
      filteredList = filteredList.where((data) {
        DateTime dateTime = DateTime.parse(data["createdAt"]!);
        return dateTime.isAfter(DateTime(
                firstDay!.year, firstDay!.month, firstDay!.day, 0, 0, 0, 0)) &&
            dateTime.isBefore(DateTime(
                lastDay!.year, lastDay!.month, lastDay!.day + 1, 0, 0, 0, 0));
      }).toList();
    }
  }

  // qr 관련 기능 시에 호출된다.
  Future<void> clickedQr(BuildContext context) async {
    final response = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const GetQr(),
      ),
    );
    if (response != null) {
      controller.text = response;
      insertedText = response;
      _filterStrings(true);
      notifyListeners();
    }
  }

  // 데이터 호출
  Future<void> _fetchData() async {
    try {
      List<dynamic>? jsonData =
          await RemoteDataSource.getUserMeatData(userModel.userId!);

      if (jsonData == null) {
        print('데이터 없음');
        throw Error();
      } else {
        // 각 사용자별로 데이터를 순회하며 id와 statusType 값을 추출하여 리스트에 추가
        for (var item in jsonData) {
          String id = item["id"];
          String statusType = item["statusType"];
          String createdAt = item["createdAt"];
          String dayTime =
              DateFormat('yyyy.MM.dd').format(DateTime.parse(createdAt));
          Map<String, String> idStatusPair = {
            "id": id,
            "statusType": statusType,
            "createdAt": createdAt,
            "dayTime": dayTime,
          };

          numList.add(idStatusPair);
        }
      }
    } catch (e) {
      print("에러발생: $e");
    }
  }

  // 관리 번호 검색 시에 호출된다.
  void onChanged(String? value) {
    isLoading = true;
    notifyListeners();

    insertedText = value ?? '';
    _filterStrings(false);

    isLoading = false;
    notifyListeners();
  }

  // 입력 텍스트 초기화 시에 호출된다.
  void textClear(BuildContext context) {
    FocusScope.of(context).unfocus();
    controller.clear();
    onChanged(null);
  }

  // 데이터 필드를 클릭 시에 호출된다.
  Future<void> onTap(int idx, BuildContext context) async {
    String id = '';

    id = selectedList[idx]["id"]!;

    try {
      isLoading = true;
      notifyListeners();
      dynamic response = await RemoteDataSource.getMeatData(id);
      if (response == null) throw Error();
      meatModel.reset();
      meatModel.fromJson(response);
      meatModel.seqno = 0;
      print(meatModel);
      _context = context;
      _movePage();
    } catch (e) {
      print("에러발생: $e");
    }
    isLoading = false;
    notifyListeners();
  }

  // 검색어를 포함하는 문자열을 반환한다. (QR 시에도 호출된다.)
  void _filterStrings(bool isQr) {
    if (isQr = false) {
      selectedList = filteredList.where((map) {
        String id = map["id"] ?? "";
        return id.contains(insertedText);
      }).toList();
    } else {
      selectedList = numList.where((map) {
        String id = map["id"] ?? "";
        return id.contains(insertedText);
      }).toList();
    }
  }

  void _movePage() {
    _context.go('/home/data-manage-normal/edit');
  }
}
