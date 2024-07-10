// //
// //
// // 이력 번호 페이지(수정 불가!) : ViewModel
// //
// //

// import 'package:flutter/material.dart';
// import 'package:go_router/go_router.dart';
// import 'package:structure/model/meat_model.dart';

// class InsertionTraceNumNotEditableViewModel with ChangeNotifier {
//   final MeatModel meatModel;
//   InsertionTraceNumNotEditableViewModel(this.meatModel) {
//     initialize();
//   }

//   final List<String?> tableData = [];

//   // 모든 데이터 입력을 체크
//   int isAllInserted = 0;

//   // 기본 변수
//   String? traceNum;
//   String? birthYmd;
//   String? species;
//   String? sexType;
//   String? farmerNm;
//   String? farmAddr;
//   String? butcheryYmd;
//   String? gradeNum;

//   // 초기 실행 함수 : 데이터 할당
//   void initialize() {
//     if (meatModel.traceNum != null) {
//       traceNum = meatModel.traceNum;
//       birthYmd = meatModel.birthYmd;
//       species = meatModel.speciesValue;
//       sexType = meatModel.sexType;
//       farmerNm = meatModel.farmerNm;
//       farmAddr = meatModel.farmAddr;
//       butcheryYmd = meatModel.butcheryYmd;
//       gradeNum = meatModel.gradeNum;
//       tableData.addAll([
//         traceNum,
//         birthYmd,
//         species,
//         sexType,
//         farmerNm,
//         farmAddr,
//         butcheryYmd,
//         gradeNum
//       ]);
//       isAllInserted = 1;
//     }
//   }

//   void clickedNextButton(BuildContext context) {
//     context.go('/home/data-manage-normal/edit/trace/info');
//   }
// }
