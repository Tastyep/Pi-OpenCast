function message(msg, importance) {
	$("#message").html("");
	$("#message").show("slow");
	if (importance === 1) {
		$("#message").html("<p class='bg-success'>"+msg+"</p>");
	} else if (importance === 2) {
		$("#message").html("<p class='bg-danger'>"+msg+"</p>");
	} else {
		$("#message").html("<p class='bg-info'>"+msg+"</p>");
	}
	setTimeout(function() {
		$("#message").hide("slow");
	}, 3000);
}

function showHistory() {
	//Only update history when div is being toggled ON
	if (!$("#history-div").is(":visible"))
		updateHistoryDiv();

	$("#history-div").toggle("fast");
}

function mkRequest(url, onSuccess) {
	url = document.location.origin + url;

	var req = new XMLHttpRequest();
	req.open("GET", url, true);
	req.onreadystatechange = function (aEvt) {
		if (this.readyState === 4) {
			if (this.status === 200) {
				var jsonData = JSON.parse(this.responseText);
				typeof onSuccess === 'function' && onSuccess(jsonData);
			} else {
				message("Error: " + req.statusText, 2);
			}
		}
	}
	req.send(null);
}

$(function() {
	$("#cast-btn").click(function() {
		var url = $("#media-url").val();
		if (url === "") {
			message("You must enter a link !", 2)
			return
		}

		message("Trying to get video metadata. Please wait ~10 seconds.", 0);
		var encodedURL = encodeURIComponent(url);
		addToHistory(url);
		mkRequest("/stream?url=" + encodedURL, function(jsonData) {
			message("Success! Video will start to play", 1);
		})
	});

	$("#queue-btn").click(function() {
		var url = $("#media-url").val();
		if ( url === "") {
			message("You must enter a link !", 2)
			return
		}

		message("Adding video to queue.", 0);
		var encodedURL = encodeURIComponent(url);
		mkRequest("/queue?url=" + encodedURL, function(jsonData) {
			message("Success! Video has been added to queue.", 1);
		})
	});

	$("#clear-search").click(function(){
		$("#media-url").val('');
		$("#clear-search").hide();
	});

	$("#media-url").keyup(function(){
		if ($(this).val()) {
			$("#clear-search").show();
		} else {
			$("#clear-search").hide();
		}
	});

	$("#pause-btn").click(function() {
		mkRequest("/video?control=pause")
	});
	$("#stop-btn").click(function() {
		mkRequest("/video?control=stop")
	});

	$("#vol-down-btn").click(function() {
		mkRequest("/sound?vol=less");
	});
	$("#vol-up-btn").click(function() {
		mkRequest("/sound?vol=more");
	});

	$("#backward-btn").click(function() {
		mkRequest("/video?control=left");
	});
	$("#forward-btn").click(function() {
		mkRequest("/video?control=right");
	});

	$("#long-backward-btn").click(function() {
		mkRequest("/video?control=longleft");
	});
	$("#long-forward-btn").click(function() {
		mkRequest("/video?control=longright");
	});

	$("#prev-video-btn").click(function() {
		mkRequest("/video?control=prev", function(jsonData) {
			message("Success! Previous video will start to play", 1);
		})
	});
	$("#next-video-btn").click(function() {
		mkRequest("/video?control=next", function(jsonData) {
			message("Success! Next video will start to play", 1);
		})
	});
});
