$(function () {
    // 通过url解析出仓库id，获取仓库信息
    var queryParams = getQueryParams();
    var houseId = queryParams['house'];
    // console.log(houseId);
    // 请求仓库详情
    $.ajax({
        url: host + 'delivery/storehouse/' + houseId + '/',
        type:'get',
        success: function (res) {
            var res = res.data;
            if (isEmpty(res)){
                $('.shDetail').html('*无此仓库相关数据')
                return false;
            }
            // 渲染数据
            var houseDetail = "<span>【"+ res.name +"】</span>";
            houseDetail += "<ul><li>到达站、港："+res.arrived+"</li>";
            houseDetail += "<li>升贴水："+res.premium+"</li>";
            houseDetail += "<li>升贴水："+res.premium+"</li>";
            houseDetail += "<li>存放地址："+res.address+"</li>";
            houseDetail += "<li>联系人："+res.link+"</li>";
            houseDetail += "<li>电话："+res.tel_phone+"</li>";
            houseDetail += "<li>传真："+res.fax+"</li></ul>";
            $('.shDetail').html(houseDetail);

            // 仓单数据
            var reportTitle = ['日期','仓库', '昨日仓单','今日仓单', '增减'];
            var tablesName = "<div>「仓单信息」</div>";
            var tableContent = '';
            $.each(res.reports, function (variety, vreport) {
                tableContent += "<table cellspacing='1' >";
                tableContent += '<span>品种：'+variety+'</span><tr>';
                $.each(reportTitle, function (index, value) {
                    tableContent += '<th>' + value + '</th>';
                });
                $.each(vreport, function (rindx, report) {
                    tableContent += '</tr><tr>';
                    tableContent += "<td>" +report.date + "</td>";
                    tableContent += "<td>" +report.house_name + "</td>";
                    tableContent += "<td>" +report.yesterday_report + "</td>";
                    tableContent += "<td>" +report.today_report + "</td>";
                    tableContent += "<td>" +report.regulation + "</td>";
                    tableContent += '</tr>';
                });
            });


            // var tableContent = "<table cellspacing='1' >";
            // tableContent += '<span>「仓单」</span><tr>';
            // $.each(reportTitle, function (index, value) {
            //     tableContent += '<th>' + value + '</th>';
            // });
            // $.each(reports, function (rindx, report) {
            //     tableContent += '</tr><tr>';
            //     tableContent += "<td>" +report.date + "</td>";
            //     tableContent += "<td>" +report.house_name + "</td>";
            //     tableContent += "<td>" +report.yesterday_report + "</td>";
            //     tableContent += "<td>" +report.today_report + "</td>";
            //     tableContent += "<td>" +report.regulation + "</td>";
            //     tableContent += '</tr>';
            // });
            $('.daily-report').html(tablesName + tableContent);
        },
        error: function (res) {
            console.log(res)
        }
    });

    // 返回按钮
    $('.backward').click(function () {
        parent.history.back();
    })
});

// 获取url查询参数集
function getQueryParams() {
	var regexpParam = /\??([\w\d%]+)=([\w\d%]*)&?/g; // 分离参数的正则表达式
	var paramMap={}; // 置空
    var url = window.location.href; // 取得iframe的url
    var ret;
    // 开始循环查找url中的参数，并以键值对形式放入结果集
    while((ret = regexpParam.exec(url)) != null) {
        // ret[1]是参数名，ret[2]是参数值
        paramMap[ret[1]] = ret[2];
    }
	return paramMap;
}

// 判空
function isEmpty(obj) {
	for (var o in obj){
		return false
	}
	return true
}