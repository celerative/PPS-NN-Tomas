const input_len = 30
const output_len = 5
var pred_in = null;
var pred_out = null;
var model = null

function initModel()
{
  //cargar modelo
  this.model = new KerasJS.Model({
    filepath: 'car_race_model.bin',
    filesystem: true,
    gpu: true
  })
  this.model.ready()
}

function testModel()
{
  //setear pred_in en 0
  this.pred_in = new Float32Array([ .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0])
  this.pred_out = new Float32Array([.0, .0, .0, .0, .0])
  //cargar pred_in con los enemigos y el jugador
  //for (var i = 0; i < this.input_len ; i++) {
  //  this.pred_in[i] =
  const inputData = {
    input: this.pred_in
  }
  console.log(inputData);
  console.log(this.pred_out);
  //predict from input
  this.model
  .predict(inputData)
  .then(outputData => {
    this.pred_out = new Float32Array(outputData.output)
    console.log(this.pred_in);
    console.log(this.pred_out);
    $("#out0").text(this.pred_out[0])
    $("#out1").text(this.pred_out[1])
    $("#out2").text(this.pred_out[2])
    $("#out3").text(this.pred_out[3])
    $("#out4").text(this.pred_out[4])
  })
  .catch(err => {
    // handle error
    console.log(err);
  })


}

window.onload = initModel;
