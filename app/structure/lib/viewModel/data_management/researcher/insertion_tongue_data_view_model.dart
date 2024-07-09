//
//
// 전자혀 데이터 ViewModel
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';

class InsertionTongueDataViewModel with ChangeNotifier {
  MeatModel meatModel;
  InsertionTongueDataViewModel(this.meatModel) {
    _initialize();
  }
  bool isLoading = false;

  // 컨트롤러
  TextEditingController sourness = TextEditingController();
  TextEditingController bitterness = TextEditingController();
  TextEditingController umami = TextEditingController();
  TextEditingController richness = TextEditingController();

  // 초기 값 할당 (모델에 값이 존재하면 할당)
  void _initialize() {
    sourness.text = meatModel.probexptData?["sourness"] == null
        ? ''
        : meatModel.probexptData!["sourness"].toString();
    bitterness.text = meatModel.probexptData?["bitterness"] == null
        ? ''
        : meatModel.probexptData!["bitterness"].toString();
    umami.text = meatModel.probexptData?["umami"] == null
        ? ''
        : meatModel.probexptData!["umami"].toString();

    richness.text = meatModel.probexptData?["richness"] == null
        ? ''
        : meatModel.probexptData!["richness"].toString();
  }

  late BuildContext _context;

  // 데이터를 객체에 할당 - 이후 POST
  Future<void> saveData(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    // 인스턴스 데이터 업데이트
    meatModel.probexptData ??= {};
    meatModel.probexptData!['updatedAt'] = Usefuls.getCurrentDate();
    meatModel.probexptData!['period'] = Usefuls.getMeatPeriod(meatModel);
    meatModel.probexptData!['sourness'] =
        sourness.text.isNotEmpty ? double.parse(sourness.text) : null;
    meatModel.probexptData!['bitterness'] =
        bitterness.text.isNotEmpty ? double.parse(bitterness.text) : null;
    meatModel.probexptData!['umami'] =
        umami.text.isNotEmpty ? double.parse(umami.text) : null;
    meatModel.probexptData!['richness'] =
        richness.text.isNotEmpty ? double.parse(richness.text) : null;
    // 완료 검사
    meatModel.checkCompleted();

    try {
      dynamic response = await RemoteDataSource.sendMeatData(
          'probexpt-data', meatModel.toJsonProbexpt());
      if (response == null) {
        throw Error();
      } else {
        _context = context;
        _movePage();
      }
    } catch (e) {
      print("에러발생: $e");
    }

    isLoading = false;
    notifyListeners();
  }

  void _movePage() {
    if (meatModel.seqno == 0) {
      // 원육
      _context.go('/home/data-manage-researcher/add/raw-meat');
    } else {
      // 처리육
      _context.go('/home/data-manage-researcher/add/processed-meat');
    }
  }
}
