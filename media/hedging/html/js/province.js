$(function () {
    var queryParams = getQueryParams();  // 获取查询参数集
    var province = queryParams['province'];
    console.log('选择' + province);
    // 获取地区下的仓库
    $.ajax({
        url: host + 'storehouse/' + province + '/',
        type: 'get',
        success: function (res) {
            console.log(res);
            if (isEmpty(res)){
                $('.ware-house').html("<div>*无相关数据</div>");
				return false;
            }
            // 渲染数据
            var houseContent = "<span>【"+res.province+"】交割库("+res.count+"家)</span>";
            delete res['count'];
            delete res['province'];
            $.each(res, function (key, value) {
                houseContent += "<div class='house-leader'>"+key+"<span class='pcount'>「交割库 "+value.length +" 家」</span></div>";
                houseContent += "<div class='house-list'>";
                houseContent += "<ul>";
                $.each(value, function (vindex, house) {
                    houseContent += "<li data-value="+house.id+">"+house.name+"</li>";
                });
                houseContent += "</ul></div>";
            });

            $('.ware-house').html(houseContent)
        },
        error: function (res) {
            console.log(res)
        }
    });

    // 品种仓库折叠展开
    $('.ware-house').on('click','.house-leader', function () {
        $(this).next().toggle();
        // $(this).sibling().next().slideUp('fast');
        adjustFrameSize()  // 改变frame大小
    });

    // 点击仓库跳转详情
	$('.ware-house').on('click', 'li', function () {
		var houseId = $(this).data('value');
		window.location.href='storehouse.html?house=' + houseId;
		parent.$('html,body').animate({scrollTop:'0px'},300);
    })
});

// 调整frame大小
function adjustFrameSize() {
	var targetEle = parent.$("#frame"); // 寻找frame目标
	targetEle.css('height', targetEle.contents().height() + 'px')
}

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

// 判空
function isEmpty(obj) {
	for (var o in obj){
		return false
	}
	return true

}