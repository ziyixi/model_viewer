<template>
  <div>
    <el-container>
      <el-header
        >Model viewer for EARA2020 (East Asia Radially Anisotropic Model
        2020)</el-header
      >
      <el-main>
        <el-row type="flex" class="row-bg" justify="center">
          <el-col :span="15">
            <!-- map -->
            <el-card
              v-loading="loadingmap"
              element-loading-text="It may take several seconds depending on your netspeed."
            >
              <div slot="header">
                <span> Map of our simulation region </span>
              </div>
              <el-image
                :src="urlmap"
                fit="fill"
                id="map"
                :preview-src-list="[urlmap]"
              ></el-image>
            </el-card>
            <!-- vertical cross-section  -->
            <el-card>
              <div slot="header">
                <span> Vertical cross-section based on your choice </span>
              </div>
              <el-image
                :src="urlvc"
                fit="fill"
                id="map"
                :preview-src-list="[urlvc]"
              ></el-image>
            </el-card>
          </el-col>
          <el-col :span="9">
            <!-- step bar  -->
            <el-card>
              <el-steps :active="current_step" align-center>
                <el-step
                  title="Step 1"
                  description="Set the great circle line you want to plot the vertical cross-section"
                ></el-step>
                <el-step
                  title="Step 2"
                  description="Configure the vertical cross-section"
                ></el-step>
              </el-steps>
            </el-card>
            <!-- map form  -->
            <el-card>
              <div slot="header">
                <span> Set the line on the map </span>
              </div>
              <el-form ref="formmap" :model="formmap">
                <el-form-item label="Starting point location">
                  <div style="display: flex">
                    <el-input
                      placeholder="Longitude (°)"
                      v-model="formmap.startlon"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                    <el-input
                      placeholder="Latitude (°)"
                      v-model="formmap.startlat"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                  </div>
                </el-form-item>
                <el-form-item label="Ending point location ">
                  <div style="display: flex">
                    <el-input
                      placeholder="Longitude (°)"
                      v-model="formmap.endlon"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                    <el-input
                      placeholder="Latitude (°)"
                      v-model="formmap.endlat"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    plain
                    @click="onsubmitmap"
                    :disabled="current_step !== 0"
                    >Submit</el-button
                  >
                  <el-button
                    type="info"
                    plain
                    @click="onclearmap"
                    :disabled="current_step !== 0"
                    >Reset</el-button
                  >
                </el-form-item>
              </el-form>
            </el-card>
            <!-- vc form  -->
            <el-card>
              <div slot="header">
                <span> Configure vertical-cross-section plotting </span>
              </div>
              <el-form ref="formvc" :model="formvc">
                <el-form-item label="Parameter">
                  <el-select
                    v-model="formvc.parameter"
                    placeholder="Select parameter"
                    :disabled="current_step !== 1"
                  >
                    <el-option
                      v-for="item in vcoptions.parameter"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                      :disabled="current_step !== 1"
                    >
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="X axis label">
                  <el-select
                    v-model="formvc.x_axis_label"
                    placeholder="Select label"
                    :disabled="current_step !== 1"
                  >
                    <el-option
                      v-for="item in vcoptions.x_axis_label"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    >
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <div>
                    <span>Depth for the vertical cross-section (km)</span>
                    <el-slider
                      v-model="formvc.depth"
                      :min="100"
                      :max="1500"
                      show-input
                      :disabled="current_step !== 1"
                    >
                    </el-slider>
                  </div>
                  <div>
                    <span>The range of colorbar (%)</span>
                    <el-slider
                      v-model="formvc.colorbar_range"
                      range
                      :max="10"
                      :min="-10"
                      :step="0.5"
                      :disabled="current_step !== 1"
                    >
                    </el-slider>
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    plain
                    @click="onsubmitvc"
                    :disabled="current_step !== 1"
                    >Submit</el-button
                  >
                  <el-button
                    type="info"
                    plain
                    @click="onclearvc"
                    :disabled="current_step !== 1"
                    >Reset</el-button
                  >
                  <el-button
                    type="info"
                    plain
                    @click="onbackvc"
                    :disabled="current_step !== 1"
                    >Back to Step1</el-button
                  >
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
      <el-footer>Footer</el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  data() {
    return {
      vcoptions: {
        parameter: [
          { value: "vp", label: "vp" },
          { value: "vs", label: "vs" },
          { value: "vpv", label: "vpv" },
          { value: "vph", label: "vph" },
          { value: "vsv", label: "vsv" },
          { value: "vsh", label: "vsh" },
        ],
        x_axis_label: [
          { label: "Longitude", value: "lon" },
          { label: "Latitude", value: "lat" },
          { label: "Great Circle Distance", value: "dist" },
        ],
      },
      urlmap: require("~/assets/basemap.png"),
      urlvc: require("~/assets/basevc.png"),
      formmap: {
        startlon: null,
        startlat: null,
        endlon: null,
        endlat: null,
      },
      formvc: {
        parameter: null,
        x_axis_label: null,
        depth: 1000,
        colorbar_range: [-3, 3],
      },
      current_step: 0,
      loadingmap: false,
    };
  },
  methods: {
    onsubmitmap() {
      this.loadingmap = true;
      this.current_step = 1;
      this.requestMap();
    },
    onclearmap() {
      for (var each_key in this.formmap) {
        this.formmap[each_key] = null;
      }
    },
    onsubmitvc() {},
    onclearvc() {
      this.formvc = {
        parameter: null,
        x_axis_label: null,
        depth: 1000,
        colorbar_range: [-3, 3],
      };
    },
    onbackvc() {
      this.current_step = 0;
    },
    // user defined functions
    async requestMap() {
      var response = await this.$axios.post("/map", this.formmap);
      if (response.data === null) {
        this.$message.error(
          "Please place the starting or ending point inside the simulation region (magenta box)"
        );
        this.loadingmap = false;
        this.current_step = 0;
      } else if (response.data === "typeerror") {
        this.$message.error(
          "Please Use the correct type (float) of the coordinates"
        );
        this.loadingmap = false;
        this.current_step = 0;
      } else {
        this.urlmap = this.$config.mapServer + response.data;
        this.loadingmap = false;
      }
    },

    // async requestMap() {
    //   var response = await this.$axios.post("/map", this.formmap);
    //   var responseBlob = new Blob([response.data], { type: "image/png" });
    //   // console.log(reader, reader.result);
    //   console.log(response.data);
    //   // this.urlmap = await this.readAsDataURLAsync(responseBlob);
    //   this.urlmap =
    //     "data:image/gif;base64,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";
    //   console.log(this.urlmap);
    // },
    // // utils
    // readAsDataURLAsync(responseBlob) {
    //   return new Promise((resolve, reject) => {
    //     let reader = new window.FileReader();

    //     reader.onload = () => {
    //       resolve(reader.result);
    //     };

    //     reader.onerror = reject;

    //     reader.readAsDataURL(responseBlob);
    //   });
    // },
  },
};
</script>

<style>
.el-header,
.el-footer {
  background-color: #ffffff;
  color: #333;
  text-align: center;
  line-height: 60px;
  font-size: 25px;
}

.el-main {
  background-color: #ffffff;
  color: #333;
  text-align: center;
  /* line-height: 560px; */
}

/* .row-bg {
  height: 1160px;
} */

/* #map {
  height: 820px;
} */
</style>
