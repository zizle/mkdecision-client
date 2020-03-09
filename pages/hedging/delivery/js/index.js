$(function () {
    new QWebChannel(qt.webChannelTransport, function(channel){
        var pageContact = channel.objects.pageContactChannel;
        window.pageChannel = pageContact;
        pageContact.senderUserToken.connect(function (userToken) {
            localStorage.token = userToken;  // 设置token，存入本地存储
            token = localStorage.token;
            pageContact.hasReceivedUserToken(true);  // 告诉界面收到了token
        });
    });

    // 获取交易所数据(品种,服务内容等)
    $.ajax({
        url: host + 'exchanges/',
        type: 'get',
        success: function (res) {
            var varietyBlock = "";
            // var serviceGuideBlock = "";
            $.each(res.data, function (eindx, exchange) {
                // 每一个交易所一个li标签
                varietyBlock += "<li>";
                // serviceGuideBlock += "<li>";
                // 遍历交易所品种
                if (eindx == 0){
                    varietyBlock += "<span class='initExchange' data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    varietyBlock += "<ul class='belong-exchange' style='display: block;'>";
                    // serviceGuideBlock += "<span class='initExchange' data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    // serviceGuideBlock += "<ul class='belong-exchange hedging-guide' style='display: block;'>";
                }else{
                    varietyBlock += "<span data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    varietyBlock += "<ul class='belong-exchange'>";
                    // serviceGuideBlock += "<span data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    // serviceGuideBlock += "<ul class='belong-exchange hedging-guide'>";
                }
                $.each(exchange.varieties, function (vindx, variety) {
                    varietyBlock += "<li data-value="+variety.name_en+">" + variety.name+"</li>"
                });
                // $.each(exchange.service_guides, function (sindx, guide) {
                //     serviceGuideBlock += "<li data-value='"+guide.en_code+"'>"+guide.name+ "</li>"
                // });
                varietyBlock += "</ul>";
                varietyBlock += "</li>";
                // serviceGuideBlock += "</ul>";
                // serviceGuideBlock += "</li>";
            });
            $('.variety-show').html(varietyBlock);
            // $('.guide').html(serviceGuideBlock);
        },
        error: function (res) {
            // console.log(res)
        }
    });

    // 填写地区
    var areaEle = "";
    $.each(areaJson, function (aindx, area) {
        var areaName = area.name;
        if(area.name.length > 3){
            areaName = area.s_name;
        }
        areaEle += "<li data-value="+area.name+">" + areaName + "</li>";
    });
    $('.province-show').html(areaEle);

    // 点击横向菜单显示菜单下的内容(主菜单)
    $('.nav').on('click', 'a', function () {
        var clickOption = $(this).data('category');
        if (clickOption == 'map'){
            $('#frame').attr('src', 'map.html');
            // 设置高度
            $('#frame').load(function () {
                $('#frame').css('height', $('#frame').contents().height() + 'px')
            })
        }else {
            var next = $(this).next();
            // next.css('display', 'block')
            next.toggle()
        }
        $(this).parent().siblings().children('.nav-show').hide();
    });
    // 悬浮交易所显示相应品种
    $('.variety-show').on('hover', 'span', function () {
        $(this).attr('class', 'initExchange');
        var next = $(this).next();
        next.show();
        // 其他交易所的隐藏
        $(this).parent().siblings().children('.belong-exchange').hide();
        $(this).parent().siblings().children('span').removeAttr('class')

    });
    // 点击品种的子菜单选项
    $('.variety-show').on('click', 'li', function (e) {
        e.stopPropagation();
        var whichExchange = $(this).parent().prev().data('value');
        var current_variety = $(this).data('value');
        if (typeof (whichExchange)=="undefined" || typeof (current_variety) == "undefined"){return false}
        $('.nav-show').slideUp('fast');
        $('#frame').attr('src', 'variety.html?exchange=' + whichExchange + '&selected=' + current_variety);
    });
    // 点击地区的省份
    $('.province-show').on('click', 'li', function () {
       $('.nav-show').slideUp('fast');
        var current_province = $(this).data('value');  // 当前省份
        // alert(current_province)
        $('#frame').attr('src', 'province.html?province=' + current_province);
    });
    //  悬浮服务指引的内容项
    $('.guide-li').on('hover', 'span', function () {
        $(this).attr('class', 'initExchange');
        var next = $(this).next();
        next.show();
        // 其他选项的隐藏
        $(this).parent().siblings().children('.hedging-guide').hide();
        $(this).parent().siblings().children('span').removeAttr('class')

    })
    // 点击服务指引
    $('.hedging-guide').on('click', 'li', function () {
        // 获取文件名称
        var fileUrl = host + 'mkDecision/hedging/delivery/guide/' +$(this).text() + ".pdf";
        // 发出信号到界面
        window.pageChannel.uiWebgetInfoFile(fileUrl);
        var whichExchange = $(this).parent().prev().data('value');
        var current_service = $(this).data('value');
        if (typeof (whichExchange)=="undefined" || typeof (current_service) == "undefined"){return false}
        // 传出信号到界面
        new QWebChannel(qt.webChannelTransport, function (channel) {
            var channelObj = channel.objects.messageChannel;
            channelObj.serviceGuide([whichExchange, current_service]);  // 通道对象信号槽函数
        });
    });


    // 最新讨论交流
    $.ajax({
        url: host + 'delivery/questions/',
        type: 'get',
        success: function (res) {
            // console.log(res);
            showLastedQuestion(res.data)
        },
        error: function (res) {
            console.log(res);
            showLastedQuestion([])
        }
    });
    // 讨论交流展开
    $('.communication').on('click', '.question', function () {
        $(this).next().toggle('fast');
        $(this).parent().siblings().children('.question').next().slideUp('fast')
    });
    // 点击讨论交流的[更多]传出信号,新跳页面
    $('.communication').on('click', 'a', function () {
        window.pageChannel.moreCommunication(true);
    });
    // 品种模式frame内请求文件转化为这里的点击事件
    $('#varietyBaseFile').click(function (e) {
        e.preventDefault();
        var fileUrl = $(this).children("input").val();
        // alert(fileUrl);
        //  发出信息通道到主UI界面
        window.pageChannel.uiWebgetInfoFile(fileUrl);
        $(this).children("input").val('');
    });
    // 初始化显示中国地图
    $('.map').click();

    // 搜索
    $('.navSearch').on('click', 'button', function () {
        // frame加载地图页
        var keyword = $(this).prev('input').val();
        $("#frame")[0].contentWindow.reloadMap(keyword);  // 调用iframe页面里的函数
        // $('.map').click();
    })

    $(".nav").on('click', '.linkUs', function () {
        window.pageChannel.toLinkUsPage(true);
    });
});


// 展示最新讨论数据
function showLastedQuestion(questions) {
    var firstEle = $('.communication').children(':first');
    $('.communication').html('');
    $('.communication').append(firstEle);
    if (!questions.length){
        var noData = "<div class='noData'>*暂无数据</div>";
        $('.communication').append(noData);
    }
    var communicationList = "";
    $.each(questions, function (qindx, question) {
        var answers = question['answers'];
        var communicationElem = "<div class='communication-item'>";
        communicationElem += "<div class='question'>";
        communicationElem += "<div class='question-title'>"+question['content']+"</div>";
        communicationElem += "<div class='question-date'>"+ question['create_time']+"</div>";
        communicationElem += "<div class='question-reply'>回复:"+answers.length+"</div>";
        communicationElem += "</div>";
        // 问题的答案
        communicationElem += "<div class='answer'>";
        $.each(answers, function (aindx, answer) {
            var floor = aindx + 1;
            var answerer = answer['answerer'];
            var answererNickName = '未知'
            if (answerer){
                answererNickName = answerer['nick_name'] || answerer['username']
            }
            communicationElem += "<div class='answerAuthor'><img src="+answerer['avatar']+" alt='头像'>&nbsp;&nbsp;"+answererNickName+"</div>";
            communicationElem += "<div class='answer-item'>";
            communicationElem += "<div class='answer-title'>"+answer['content']+"</div>";
            communicationElem += "<div class='answer-date'>"+answer['create_time']+"</div>";
            communicationElem += "<div class='answer-floor'>#"+floor+"楼</div>";
            communicationElem += "</div>" ;
        });
        communicationElem += "</div>";
        communicationElem += "</div>";
        communicationList += communicationElem;
        if (qindx == 4){  // 控制显示的条数
            return false
        }
    });
    $('.communication').append(communicationList)
    // 轮询设置页面高度
    window.setInterval("reinitIframe()", 300)
}

function reinitIframe(){

var iframe = document.getElementById("frame");
    iframe.height = 0; //只有先设置原来的iframe高度为0，之前的iframe高度才不会对现在的设置有影响
    try{
    var bHeight = iframe.contentWindow.document.body.scrollHeight;
    var dHeight = iframe.contentWindow.document.documentElement.scrollHeight;
    var height = Math.max(bHeight, dHeight);
    iframe.height = height;
    $('#frame').css('height', height);
    // console.log(height);
    }catch (ex){}
}
