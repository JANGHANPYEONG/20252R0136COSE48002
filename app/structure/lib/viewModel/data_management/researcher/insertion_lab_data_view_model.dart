//
//
// 실험 데이터(ViewModel) : Researcher
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class InsertionLabDataViewModel with ChangeNotifier {
  MeatModel meatModel;
  UserModel userModel;
  bool isRaw;
  BuildContext context;
  InsertionLabDataViewModel(
      this.meatModel, this.userModel, this.isRaw, this.context) {
    _initialize();
  }
  bool isLoading = false;
  String title = '실험 데이터';

  final GlobalKey<FormState> formKey = GlobalKey<FormState>();

  // 컨트롤러
  TextEditingController l = TextEditingController();
  TextEditingController a = TextEditingController();
  TextEditingController b = TextEditingController();
  TextEditingController dl = TextEditingController();
  TextEditingController cl = TextEditingController();
  TextEditingController rw = TextEditingController();
  TextEditingController ph = TextEditingController();
  TextEditingController wbsf = TextEditingController();
  TextEditingController ct = TextEditingController();
  TextEditingController mfi = TextEditingController();
  TextEditingController collagen = TextEditingController();

  bool inputComplete = false;

  // 초기 할당 : 모델에 값이 있다면 불러옴.
  void _initialize() {
    if (isRaw) {
      l.text = '${meatModel.probExpt?['L'] ?? ''}';
      a.text = '${meatModel.probExpt?['a'] ?? ''}';
      b.text = '${meatModel.probExpt?['b'] ?? ''}';
      dl.text = '${meatModel.probExpt?['DL'] ?? ''}';
      cl.text = '${meatModel.probExpt?['CL'] ?? ''}';
      rw.text = '${meatModel.probExpt?['RW'] ?? ''}';
      ph.text = '${meatModel.probExpt?['ph'] ?? ''}';
      wbsf.text = '${meatModel.probExpt?['WBSF'] ?? ''}';
      ct.text = '${meatModel.probExpt?['cardepsin_activity'] ?? ''}';
      mfi.text = '${meatModel.probExpt?['MFI'] ?? ''}';
      collagen.text = '${meatModel.probExpt?['Collagen'] ?? ''}';

      if (meatModel.seqno == 0) {
        title = '원육 실험 데이터';
      } else {
        title = '처리육 실험 데이터';
      }
    } else {
      l.text = '${meatModel.heatedProbExpt?['L'] ?? ''}';
      a.text = '${meatModel.heatedProbExpt?['a'] ?? ''}';
      b.text = '${meatModel.heatedProbExpt?['b'] ?? ''}';
      dl.text = '${meatModel.heatedProbExpt?['DL'] ?? ''}';
      cl.text = '${meatModel.heatedProbExpt?['CL'] ?? ''}';
      rw.text = '${meatModel.heatedProbExpt?['RW'] ?? ''}';
      ph.text = '${meatModel.heatedProbExpt?['ph'] ?? ''}';
      wbsf.text = '${meatModel.heatedProbExpt?['WBSF'] ?? ''}';
      ct.text = '${meatModel.heatedProbExpt?['cardepsin_activity'] ?? ''}';
      mfi.text = '${meatModel.heatedProbExpt?['MFI'] ?? ''}';
      collagen.text = '${meatModel.heatedProbExpt?['Collagen'] ?? ''}';

      title = '가열육 실험 데이터';
    }
  }

  /// 모든 필드가 입력 되었는지 확인하는 함수
  void inputCheck() {
    inputComplete = l.text.isNotEmpty &&
        a.text.isNotEmpty &&
        b.text.isNotEmpty &&
        dl.text.isNotEmpty &&
        cl.text.isNotEmpty &&
        rw.text.isNotEmpty &&
        ph.text.isNotEmpty &&
        wbsf.text.isNotEmpty &&
        ct.text.isNotEmpty &&
        mfi.text.isNotEmpty &&
        collagen.text.isNotEmpty &&
        formKey.currentState!.validate();
  }

  // 데이터를 객체에 할당 - 이후 POST
  Future<void> saveData() async {
    isLoading = true;
    notifyListeners();

    // probExpt가 없으면 post로 진행해야 함
    bool isPost = false;

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
      // 실험 데이터 입력
      meatModel.probExpt!['L'] = double.parse(l.text);
      meatModel.probExpt!['a'] = double.parse(a.text);
      meatModel.probExpt!['b'] = double.parse(b.text);
      meatModel.probExpt!['DL'] = double.parse(dl.text);
      meatModel.probExpt!['CL'] = double.parse(cl.text);
      meatModel.probExpt!['RW'] = double.parse(rw.text);
      meatModel.probExpt!['ph'] = double.parse(ph.text);
      meatModel.probExpt!['WBSF'] = double.parse(wbsf.text);
      meatModel.probExpt!['cardepsin_activity'] = double.parse(ct.text);
      meatModel.probExpt!['MFI'] = double.parse(mfi.text);
      meatModel.probExpt!['Collagen'] = double.parse(collagen.text);
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
      // 실험 데이터 입력
      meatModel.heatedProbExpt!['L'] = double.parse(l.text);
      meatModel.heatedProbExpt!['a'] = double.parse(a.text);
      meatModel.heatedProbExpt!['b'] = double.parse(b.text);
      meatModel.heatedProbExpt!['DL'] = double.parse(dl.text);
      meatModel.heatedProbExpt!['CL'] = double.parse(cl.text);
      meatModel.heatedProbExpt!['RW'] = double.parse(rw.text);
      meatModel.heatedProbExpt!['ph'] = double.parse(ph.text);
      meatModel.heatedProbExpt!['WBSF'] = double.parse(wbsf.text);
      meatModel.heatedProbExpt!['cardepsin_activity'] = double.parse(ct.text);
      meatModel.heatedProbExpt!['MFI'] = double.parse(mfi.text);
      meatModel.heatedProbExpt!['Collagen'] = double.parse(collagen.text);
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
      } else {
        // TODO: 입력한 데이터 삭제해야함
        throw ErrorDescription(response);
      }
    } catch (e) {
      debugPrint("Error: $e");
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }

    // 완료 검사
    meatModel.checkCompleted();

    isLoading = false;
    notifyListeners();

    if (context.mounted) context.pop();
  }

  String? validate(String? value, double min, double max) {
    double parsedValue = double.tryParse(value!) ?? 1.0;
    if (parsedValue < min || parsedValue > max) {
      return '$min~$max 사이의 값을 입력하세요.';
    }
    return null;
  }
}
