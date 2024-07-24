//
//
// 전자혀 데이터 ViewModel
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionTongueDataViewModel with ChangeNotifier {
  MeatModel meatModel;
  UserModel userModel;
  bool isRaw;
  InsertionTongueDataViewModel(this.meatModel, this.userModel, this.isRaw) {
    _initialize();
  }
  bool isLoading = false;
  late BuildContext _context;

  // 컨트롤러
  TextEditingController sourness = TextEditingController();
  TextEditingController bitterness = TextEditingController();
  TextEditingController umami = TextEditingController();
  TextEditingController richness = TextEditingController();

  // 초기 값 할당 (모델에 값이 존재하면 할당)
  void _initialize() {
    if (isRaw) {
      // 원육/처리육
      sourness.text = '${meatModel.probExpt?['sourness'] ?? ''}';
      bitterness.text = '${meatModel.probExpt?['bitterness'] ?? ''}';
      umami.text = '${meatModel.probExpt?['umami'] ?? ''}';
      richness.text = '${meatModel.probExpt?['richness'] ?? ''}';
    } else {
      // 가열육
      sourness.text = '${meatModel.heatedProbExpt?['sourness'] ?? ''}';
      bitterness.text = '${meatModel.heatedProbExpt?['bitterness'] ?? ''}';
      umami.text = '${meatModel.heatedProbExpt?['umami'] ?? ''}';
      richness.text = '${meatModel.heatedProbExpt?['richness'] ?? ''}';
    }
  }

  // 데이터를 객체에 할당 - 이후 POST
  Future<void> saveData(BuildContext context) async {
    isLoading = true;
    notifyListeners();

    // probExpt가 없으면 post로 진행해야 함
    bool isPost = false;

    // 데이터 생성
    if (isRaw) {
      // 원육/처리육
      if (meatModel.probExpt == null) {
        // POST의 경우 신규 데이터 생성
        isPost = true;

        meatModel.probExpt = {};
        meatModel.probExpt!['meatId'] = meatModel.meatId;
        meatModel.probExpt!['userId'] = userModel.userId;
        meatModel.probExpt!['seqno'] = meatModel.seqno;
      }
      // 전자혀 데이터 입력
      meatModel.probExpt!['sourness'] = double.parse(sourness.text);
      meatModel.probExpt!['bitterness'] = double.parse(bitterness.text);
      meatModel.probExpt!['umami'] = double.parse(umami.text);
      meatModel.probExpt!['richness'] = double.parse(richness.text);
    } else {
      // 가열육
      if (meatModel.heatedProbExpt == null) {
        // POST의 경우 신규 데이터 생성
        isPost = true;

        meatModel.heatedProbExpt = {};
        meatModel.heatedProbExpt!['meatId'] = meatModel.meatId;
        meatModel.heatedProbExpt!['userId'] = userModel.userId;
        meatModel.heatedProbExpt!['seqno'] = meatModel.seqno;
      }
      // 전자혀 데이터 입력
      meatModel.heatedProbExpt!['sourness'] = double.parse(sourness.text);
      meatModel.heatedProbExpt!['bitterness'] = double.parse(bitterness.text);
      meatModel.heatedProbExpt!['umami'] = double.parse(umami.text);
      meatModel.heatedProbExpt!['richness'] = double.parse(richness.text);
    }

    // API 전송
    try {
      dynamic response;

      if (isRaw) {
        // 원육/처리육
        if (isPost) {
          response = await RemoteDataSource.createMeatData(
              'probexpt-data', meatModel.toJsonProbExpt());
        } else {
          response = await RemoteDataSource.patchMeatData(
              'probexpt-data', meatModel.toJsonProbExpt());
        }
      } else {
        // 가열육
        if (isPost) {
          response = await RemoteDataSource.createMeatData(
              'probexpt-data', meatModel.toJsonHeatedProbExpt());
        } else {
          response = await RemoteDataSource.patchMeatData(
              'probexpt-data', meatModel.toJsonHeatedProbExpt());
        }
      }

      if (response == 200) {
        if (isRaw) {
          meatModel.updateProbExpt();
        } else {
          meatModel.updateHeatedProbExpt();
        }

        _context = context;
        _movePage();
      } else {
        // TODO : 입력한 데이터 초기화
        throw Error();
      }
    } catch (e) {
      debugPrint("Error: $e");
    }

    // 완료 검사
    meatModel.checkCompleted();

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
