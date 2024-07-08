import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/screen/data_management/researcher/approve_data_screen.dart';
import 'package:structure/screen/data_management/researcher/data_management_home_researcher_screen.dart';

class DataManagementHomeTabScreen extends StatefulWidget {
  const DataManagementHomeTabScreen({super.key});

  @override
  State<DataManagementHomeTabScreen> createState() =>
      _DataManagementHomeTabScreenState();
}

class _DataManagementHomeTabScreenState
    extends State<DataManagementHomeTabScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: Transform.translate(
            offset: Offset(-50.w, 0), // 왼쪽으로 이동시킬 픽셀 값
            child: Text(
              '데이터 관리',
              style: Palette.appBarTitle,
            ),
          ),
          bottom: TabBar(
            labelColor: Colors.black,
            controller: _tabController,
            tabs: const [
              Tab(text: '추가 정보 입력'),
              Tab(text: '일반데이터 승인'),
            ],
          ),
          backgroundColor: Colors.white,
        ),
        body: TabBarView(
          controller: _tabController,
          children: const [
            DataManagementHomeResearcherScreen(),
            ApproveDataScreen(),
          ],
        ));
  }
}
