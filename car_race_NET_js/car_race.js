var cvs_width = 480, cvs_height = 400;

function object(x, y)
{
    this.x = x;
    this.y = y;
}

function racing_car(x, y)
{
	this.last_x = -1;
  this.next_x = -1;
    this.x = x;
    this.y = y;
}

var ws = null;
var ctx = null;

var user_car = null;
var opponent_cars = null;
var grid = null;
var sidelines = null;
var cur_score = null;


var level_up = null;
var cur_level	= null;
var speed_default = null;
var speed_delta	= null;
var updated_speed = null;
var updated_timer = null;
var is_crashed = null;
var is_not_finished = null;

var car_width = null;
var car_height = null;
var line_width = null;
var block_size = null;
var line_distance = null;
var rect_line_width = null;
var blink_times = null;

var pred_out = null;
var model = null
var pos = 0
var run_NET = false

function init()
{

	cur_score = 0;

	level_up = 0;
	cur_level = 0;
	speed_default = 300;
	speed_delta = 20;
	updated_speed = get_speed();

	is_crashed = false;
	is_not_finished = true;
	blink_times = 0;

	var width = window.innerWidth;
	var height = window.innerHeight;

	var ratio_x = (width - 250) / cvs_width;
	var ratio_y = (height - 250) / cvs_height;
	var ratio = (ratio_x < ratio_y) ? ratio_x : ratio_y;

	cvs_width *= ratio;
	cvs_height *= ratio;

	block_size = cvs_height/24;
	car_width = 3;
	car_height = 4;

	line_width = 2*ratio;
	line_distance = 3*ratio;
	rect_line_width = 1*ratio;


	var canvas = document.getElementById("remote");
	canvas.width = cvs_width;
	canvas.height = cvs_height;
	ctx = canvas.getContext("2d");
	ctx.translate(100, 0);

	opponent_cars = [];
	for (var i = 0; i<3; i++)
	{
		opponent_cars.push(new object((Math.floor(Math.random() * 5))*car_width, -(8+2*Math.floor(Math.random()))));
		opponent_cars.push(new object((Math.floor(Math.random() * 5))*car_width, -(24+2*Math.floor(Math.random()))));
	}

	sidelines = [];

	for (var i = 0; i<7; i++)
	{
		sidelines.push(new object(-2, 4*i));
		sidelines.push(new object(16, 4*i));
	}

	user_car = new racing_car(2*car_width, 20);

	draw_car(user_car, false, true);
	draw_sideline();
	draw_grid();

  // initialize NET model
  // load model
  this.model = new KerasJS.Model({
    filepath: 'car_race_model.bin',
    filesystem: true,
    gpu: true
  })
  this.model.ready()
}


// run NET
function move_car(flag, pred)
{
  if(pred){
    pos = 0
    const inputData = {
      input: this.grid
    }
    this.model
    .predict(inputData)
    .then(outputData => {
      this.pred_out = new Float32Array(outputData.output)
      console.log(this.pred_out);
      let max = -1
      for (var i = 0; i < this.pred_out.length; i++) {
        if (this.pred_out[i] > max){
          max = this.pred_out[i]
          pos = i
        }
      }
    })
    .catch(err => {
      // handle error
      console.log(err);
    })
  }
  if(!flag) {
        setTimeout(function() {
           move_car(true, false);
        }, 50);
        return;
  }
  user_car.next_x = pos * car_width;
  while (user_car.next_x != user_car.x){
    if (user_car.next_x < user_car.x) {
      user_car.x -= car_width
      draw_car(user_car, true, true);
    }else{
      user_car.x += car_width
      draw_car(user_car, true, true);
    }
    is_crashed = check_crash();
    if (is_crashed==true)
  	{
  		//clearInterval(updated_timer);
  		blinking();
  		return;
  	}
  }
}

function get_speed()
{
	// return (speed_default - speed_delta*cur_level)
  return (200)
}


function draw_score()
{
	$("#controls").text("SCORE: " + cur_score)
}


function draw_car(obj, is_broken, is_user)
{

	ctx.save();
	ctx.translate(obj.x*block_size,obj.y*block_size);
	if (is_user == true)
	{
    ctx.fillStyle = "#5c9618";
    if (is_broken == true){
		  ctx.fillStyle = "#304a12";
    }
	}
	else
	{
		ctx.fillStyle = "#020202";
	}
  ctx.fillRect(0, block_size, 3*block_size, block_size);
  ctx.fillRect(block_size, 0, block_size, 3*block_size);
  ctx.fillRect(0, 3*block_size, block_size, block_size);
  ctx.fillRect(2*block_size, 3*block_size, block_size, block_size);

	draw_rectangle(1,0);
	draw_rectangle(1,1);
	draw_rectangle(1,2);
	draw_rectangle(0,1);
	draw_rectangle(2,1);
	draw_rectangle(0,3);
	draw_rectangle(2,3);
    ctx.restore();
}


function draw_rectangle(x,y)
{

	ctx.beginPath();
	ctx.lineWidth= rect_line_width;
	ctx.strokeStyle="#FFFFFF";
	ctx.rect(x*block_size+line_distance,y*block_size+line_distance,block_size-2*line_distance,block_size - 2*line_distance);
	ctx.stroke();
}



function draw_grid()
{

	ctx.save();
	ctx.translate(-2*block_size,0);
	ctx.lineWidth = line_width;
	ctx.strokeStyle = "#FCFCFC";

	for( var x_id = 0; x_id <= 19; x_id++)
	{
		ctx.beginPath();
		ctx.moveTo(x_id*block_size,0);
		ctx.lineTo(x_id*block_size,block_size*24);
		ctx.stroke();
	}

	for( var y_id = 0; y_id <= 24; y_id++)
	{
		ctx.beginPath();
		ctx.moveTo(0, y_id*block_size);
		ctx.lineTo(block_size*19, y_id*block_size);
		ctx.stroke();
	}
	ctx.restore();
}


function draw_sideline()
{
	var move_down = 1;
	if (is_not_finished == false)
	{
		move_down = 0;
	}
	for( var y_id = 0; y_id < 14; y_id++)
	{
		ctx.fillStyle = "#020202";
		ctx.fillRect(sidelines[y_id].x*block_size , sidelines[y_id].y*block_size , block_size, 2*block_size);
		draw_rectangle(sidelines[y_id].x,sidelines[y_id].y);
		draw_rectangle(sidelines[y_id].x,sidelines[y_id].y+1);
		sidelines[y_id].y += move_down;
		if (sidelines[y_id].y > (user_car.y + car_height))
		{
			sidelines[y_id].y -= 7*car_height;
		}
	}

}


function move_opponent_cars()
{
	for (var car_id = 0; car_id < 6; car_id++)
	{
		cur_y = opponent_cars[car_id].y;
		if (cur_y <= (user_car.y + 3))
		{
			opponent_cars[car_id].y += 1;
		}
		else
		{
			cur_score += 1;
			opponent_cars[car_id].x = (Math.floor(Math.random() * 5))*car_width;
			opponent_cars[car_id].y += (-8*car_height+1);
		}
	}

	while (shuffle_needed())
	{
		for (var car_id = 0; car_id < 5; car_id++)
		{
			for (var car_id_2nd = car_id+1; car_id_2nd < 6; car_id_2nd++)
			{

				while ((opponent_cars[car_id_2nd].y == opponent_cars[car_id].y)&&
				(Math.abs(opponent_cars[car_id_2nd].x - opponent_cars[car_id].x)<= car_width))
					{

					if (Math.random()>0.5)
					{
						opponent_cars[car_id_2nd].x = Math.floor(Math.random()* 5)*car_width;
					}
					else
					{
						opponent_cars[car_id_2nd].y -= Math.ceil(Math.random())*car_height;
					}
					}

				while ((opponent_cars[car_id_2nd].x == opponent_cars[car_id].x)&&
				(Math.abs(opponent_cars[car_id_2nd].y - opponent_cars[car_id].y)< 2*car_height))
					{
						opponent_cars[car_id_2nd].y -= Math.ceil(Math.random())*2;
					}


			}
		}

	}
  // create input for NET
  grid = new Float32Array([ .0, .0, .0, .0, .0,
                            .0, .0, .0, .0, .0,
                            .0, .0, .0, .0, .0,
                            .0, .0, .0, .0, .0,
                            .0, .0, .0, .0, .0,
                            .0, .0, .0, .0, .0])
  // locate user_car on grid
  grid[25 + Math.floor(user_car.x / car_width)] = .5
	for (var car_id = 0; car_id < 6; car_id++)
	{
    if (opponent_cars[car_id].y % 4 == 0){
      run_NET = true
    }else{
      break
    }
		if (opponent_cars[car_id].y >= 0 && opponent_cars[car_id].y < 24)
		{
			grid[Math.floor((opponent_cars[car_id].y) / car_height) * 5 + Math.floor(opponent_cars[car_id].x / car_width)] = 1
		}
	}
}


function shuffle_needed()
{
	for (var car_id = 0; car_id < 5; car_id++)
	{
		for (var car_id_2nd = car_id+1; car_id_2nd < 6; car_id_2nd++)
		{

			if ((opponent_cars[car_id_2nd].x == opponent_cars[car_id].x)&&
			(Math.abs(opponent_cars[car_id_2nd].y - opponent_cars[car_id].y)< 2*car_height))
				return true;

			if ((opponent_cars[car_id_2nd].y == opponent_cars[car_id].y)&&
			(Math.abs(opponent_cars[car_id_2nd].x - opponent_cars[car_id].x)<= car_width))
				return true;
		}
	}
	return false;
}


function check_crash()
{
	var crash_car_id = null;
	for (var car_id = 0; car_id < 6; car_id++)
	{
		cur_y = opponent_cars[car_id].y;
		if ((cur_y > (user_car.y - car_height)) && (cur_y < (user_car.y + car_height)-1))
		{

			if (((opponent_cars[car_id].x < user_car.x) && (opponent_cars[car_id].x > user_car.last_x)) ||
			((opponent_cars[car_id].x>user_car.x) && (opponent_cars[car_id].x < user_car.last_x)) || (opponent_cars[car_id].x == user_car.x))
			{

				is_not_finished = false;
				crash_car_id = car_id;

				if ((Math.abs(opponent_cars[car_id].x - user_car.last_x)) <= (Math.abs(opponent_cars[crash_car_id].x - user_car.last_x)))
				{
					crash_car_id = car_id;
					user_car.x = opponent_cars[crash_car_id].x;
				}
			}
		}
	}
	return (!is_not_finished);
}


function game_over()
{
	$("#controls").html("GAME OVER<br>SCORE: " + cur_score + '<br><button id="bt_start" type="button" onclick="loop();">START</button>')
}


function blinking()
{
	ctx.clearRect(-100, 0, cvs_width, cvs_height);

	for (var car_id = 0; car_id < 6; car_id++)
	{
		draw_car(opponent_cars[car_id], false,false);
	}

	draw_score();
	draw_sideline();
	draw_grid();

	if ((blink_times % 2)==0){
		draw_car(user_car, true, true);
	}

	if (blink_times > 4)
	{
    draw_car(user_car, true, false);
		game_over();
	}
	else
	{
		setTimeout(function(){blinking();}, 500);
		blink_times ++;
	}
}


function update_scene()
{
	if (is_not_finished == true)
	{
		ctx.clearRect(-100, 0, cvs_width, cvs_height);

		for (var car_id = 0; car_id < 6; car_id++)
		{
			draw_car(opponent_cars[car_id],false, false);
		}

		draw_car(user_car,false, true);
		draw_score();
		draw_sideline();
		draw_grid();

		user_car.last_x = user_car.x;
	}
}


function game_process()
{
		is_crashed = check_crash();

		if (is_crashed==true)
		{
			//clearInterval(updated_timer);
			blinking();

			return;
		}

		move_opponent_cars();
    if (run_NET) {
      console.log(grid)
      move_car(false, true);
      run_NET = false
    }
		update_scene();
		loop();
}

function loop()
{
	if (is_crashed==true)
	{
		init()
	}

	setTimeout(function(){game_process();}, 300);
	if (is_crashed==true)
	{
		return;
	}
}


window.onload = init;
