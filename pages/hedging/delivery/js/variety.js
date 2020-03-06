$(function () {
    // 获得随src属性传入的参数
    var queryParams = getQueryParams();  // 获取查询参数集
    // var exchange = queryParams['exchange'];
    var selected = queryParams['selected'];
    // console.log('选择了' +exchange + '的' + selected)
    // 根据参数获取相应的内容显示
	$.ajax({
		url: host + 'delivery/storehouse/' + selected + "/",
		type: 'get',
		contentType: 'application/json',
		success: function (res) {
			// console.log(res);
			var res = res.data;
			if (isEmpty(res)){
				$('.base-msg').html("<div>*无相关数据</div>");
				return false;
			}
			var baseInfo = "<ul>";
			baseInfo += "<li>交割标准(品牌)：<a href="+ host + "mkDecision/hedging/delivery/varietyFiles/" + res.exchange + res.name + res.name_en +"交割品牌.pdf>"+res.name +"交割品牌.pdf</a></li>";
			baseInfo += "<li>最后交易日："+ res.delivery_date+"</li>";
			baseInfo += "<li>最小交割单位："+ res.delivery_unit_min+"</li>";
			baseInfo += "<li>仓单有效期："+ res.warrant_expire_date+"</li>";
			baseInfo += "<li>交割费用：<a href="+ host + "mkDecision/hedging/delivery/varietyFiles/"+ res.exchange + res.name+res.name_en +"交割费用.pdf>"+ res.name +"交割费用.pdf</a></li>";
			baseInfo += "<li>质检机构：<a href="+ host + "mkdecision/hegding/delivery/varietyFiles/" + res.exchange + res.name + res.name_en +"质检机构.pdf>"+ res.name+"质检机构.pdf</a></li>";
			baseInfo +=  "</ul>";
			$('.base-msg').html(baseInfo);
			// 取出仓库数据
			var storehouses = res.storehouses;
			var houseContent = "<span>【"+ res.name+"】交割库("+storehouses.count+"家)</span>";
			delete storehouses['count'];
			$.each(storehouses, function (key, value) {
				houseContent += "<div class='house-leader'>"+key+"</div>";
				houseContent += "<div class='house-list'><ul>";
				$.each(value, function (vindx, house) {
					houseContent += "<li data-value="+house.id+">"+house.name+"</li>"
				});
				houseContent += "</ul></div>";
			});
			$('.ware-house').html(houseContent)
		},
		error: function (res) {
			console.log(res)
		}
	});

	// 基本信息里的文件被点击传出信号，UI请求显示
	$('.base-msg').on('click', 'a', function (event) {
		event.preventDefault(); // 禁止原事件
		var fileUrl = $(this).attr('href');
		// 获取父窗口的input并填值,UI交互事件得由父窗口发出
		parent.$("#varietyBaseFile").children('input').val(fileUrl);
		parent.$("#varietyBaseFile").click();
	});

    // 省份仓库折叠展开
    $('.ware-house').on('click','.house-leader', function () {
        $(this).next().toggle();
        // $(this).siblings('.house-leader').next().slideUp('fast');
        adjustFrameSize()  // 改变frame大小
    });

	// 点击仓库跳转详情
	$('.ware-house').on('click', 'li', function () {
		var houseId = $(this).data('value');
		window.location.href='storehouse.html?house=' + houseId;
		parent.$('html,body').animate({scrollTop:'0px'},300);
    })

});

// 获取url查询参数集
function getQueryParams() {
    var targetEle = parent.$("#frame"); // 寻找frame目标
	var regexpParam = /\??([\w\d%]+)=([\w\d%]*)&?/g; // 分离参数的正则表达式
	var  paramMap=null; // 置空
	if(!!targetEle) {
	    var url = targetEle.attr("src"); // 取得iframe的url
	    var ret;
	    paramMap = {}; // 初始化结果集
	    // 开始循环查找url中的参数，并以键值对形式放入结果集
	    while((ret = regexpParam.exec(url)) != null) {
	    	// ret[1]是参数名，ret[2]是参数值
	        paramMap[ret[1]] = ret[2];
	    }
	}
	return paramMap;
}

// 调整frame大小
function adjustFrameSize() {
	var targetEle = parent.$("#frame"); // 寻找frame目标
	targetEle.css('height', targetEle.contents().height() + 'px')
}

// 判空
function isEmpty(obj) {
	for (var o in obj){
		return false
	}
	return true
}

