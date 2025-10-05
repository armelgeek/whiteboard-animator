"""
Animation generation service
"""

import os
import time
import datetime
import cv2
import numpy as np
import math
from pathlib import Path
from typing import Dict, Optional
from .image_service import ImageService
from ..utils.image_utils import euc_dist


class AnimationVariables:
    """Container for animation generation variables"""
    
    def __init__(
        self,
        frame_rate: int = 30,
        resize_wd: int = 1280,
        resize_ht: int = 720,
        split_len: int = 10,
        object_skip_rate: int = 5,
        bg_object_skip_rate: int = 8,
        end_gray_img_duration_in_sec: int = 3
    ):
        self.frame_rate = frame_rate
        self.resize_wd = resize_wd
        self.resize_ht = resize_ht
        self.split_len = split_len
        self.object_skip_rate = object_skip_rate
        self.bg_object_skip_rate = bg_object_skip_rate
        self.end_gray_img_duration_in_sec = end_gray_img_duration_in_sec
        
        # These will be set during processing
        self.img = None
        self.img_gray = None
        self.img_thresh = None
        self.img_ht = None
        self.img_wd = None
        self.hand = None
        self.hand_mask = None
        self.hand_mask_inv = None
        self.hand_ht = None
        self.hand_wd = None
        self.drawn_frame = None
        self.video_object = None


class AnimationService:
    """Service for generating whiteboard animations"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize animation service
        
        Args:
            base_path: Base path for resources (defaults to api directory)
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_path = base_path
        # Try to use resources from kivy directory if available
        kivy_path = os.path.join(os.path.dirname(base_path), 'kivy')
        if os.path.exists(kivy_path):
            self.images_path = os.path.join(kivy_path, 'data', 'images')
        else:
            self.images_path = os.path.join(base_path, 'data', 'images')
        
        self.hand_path = os.path.join(self.images_path, 'drawing-hand.png')
        self.hand_mask_path = os.path.join(self.images_path, 'hand-mask.png')
    
    def create_animation(
        self,
        image_path: str,
        split_len: int = 10,
        frame_rate: int = 30,
        object_skip_rate: int = 5,
        bg_object_skip_rate: int = 8,
        main_img_duration: int = 3,
        save_path: Optional[str] = None,
        platform: str = "linux"
    ) -> Dict:
        """
        Create whiteboard animation from image
        
        Args:
            image_path: Path to input image
            split_len: Grid split length
            frame_rate: Output video frame rate
            object_skip_rate: Skip rate for object drawing
            bg_object_skip_rate: Skip rate for background drawing
            main_img_duration: Duration to show final image
            save_path: Custom save path
            platform: Target platform
            
        Returns:
            Dictionary with status, message, and video path
        """
        start_total = time.time()
        
        try:
            # Validate image path
            if not os.path.exists(image_path):
                return {
                    "status": False,
                    "message": f"Image file not found: {image_path}",
                    "video_path": None
                }
            
            # Read image
            image_bgr = cv2.imread(image_path)
            if image_bgr is None:
                return {
                    "status": False,
                    "message": f"Failed to read image: {image_path}",
                    "video_path": None
                }
            
            # Determine save path
            if save_path is None:
                save_path = os.path.join(self.base_path, "output_videos")
            os.makedirs(save_path, exist_ok=True)
            
            # Generate video filename
            now = datetime.datetime.now()
            current_time = now.strftime("%H%M%S")
            current_date = now.strftime("%Y%m%d")
            
            if platform == "android":
                video_save_name = f"vid_{current_date}_{current_time}.avi"
            else:
                video_save_name = f"vid_{current_date}_{current_time}.mp4"
            
            save_video_path = os.path.join(save_path, video_save_name)
            
            # Get optimal resolution
            img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
            aspect_ratio = img_wd / img_ht
            from ..utils.image_utils import find_nearest_res
            img_ht = find_nearest_res(img_ht)
            new_aspect_wd = int(img_ht * aspect_ratio)
            img_wd = find_nearest_res(new_aspect_wd)
            
            # Create variables object
            variables = AnimationVariables(
                frame_rate=frame_rate,
                resize_wd=img_wd,
                resize_ht=img_ht,
                split_len=split_len,
                object_skip_rate=object_skip_rate,
                bg_object_skip_rate=bg_object_skip_rate,
                end_gray_img_duration_in_sec=main_img_duration
            )
            
            # Generate animation
            self._draw_whiteboard_animation(
                image_bgr, save_video_path, variables, platform
            )
            
            # Try to convert with ffmpeg
            ffmpeg_file_name = f"vid_{current_date}_{current_time}_h264.mp4"
            ffmpeg_video_path = os.path.join(save_path, ffmpeg_file_name)
            ff_stat = self._ffmpeg_convert(save_video_path, ffmpeg_video_path, platform)
            
            if ff_stat:
                final_path = ffmpeg_video_path
                try:
                    os.unlink(save_video_path)
                except:
                    pass
            else:
                final_path = save_video_path
            
            processing_time = time.time() - start_total
            
            return {
                "status": True,
                "message": "Animation created successfully",
                "video_path": final_path,
                "processing_time": round(processing_time, 2)
            }
            
        except Exception as e:
            return {
                "status": False,
                "message": f"Error creating animation: {str(e)}",
                "video_path": None
            }
    
    def _draw_whiteboard_animation(
        self,
        img: np.ndarray,
        save_video_path: str,
        variables: AnimationVariables,
        platform: str
    ):
        """Draw whiteboard animation"""
        
        # Preprocess image
        img_data = ImageService.preprocess_image(img, variables.resize_wd, variables.resize_ht)
        variables.img = img_data["img"]
        variables.img_gray = img_data["img_gray"]
        variables.img_thresh = img_data["img_thresh"]
        variables.img_ht = img_data["img_ht"]
        variables.img_wd = img_data["img_wd"]
        
        # Preprocess hand image
        hand_data = ImageService.preprocess_hand_image(self.hand_path, self.hand_mask_path)
        variables.hand = hand_data["hand"]
        variables.hand_mask = hand_data["hand_mask"]
        variables.hand_mask_inv = hand_data["hand_mask_inv"]
        variables.hand_ht = hand_data["hand_ht"]
        variables.hand_wd = hand_data["hand_wd"]
        
        # Setup video writer
        if platform == "android":
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        else:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        
        variables.video_object = cv2.VideoWriter(
            save_video_path,
            fourcc,
            variables.frame_rate,
            (variables.resize_wd, variables.resize_ht)
        )
        
        # Create empty frame
        variables.drawn_frame = np.zeros(variables.img.shape, np.uint8) + np.array(
            [255, 255, 255], np.uint8
        )
        
        # Draw the animation
        self._draw_masked_object(variables, skip_rate=variables.object_skip_rate)
        
        # End with original image
        for i in range(variables.frame_rate * variables.end_gray_img_duration_in_sec):
            variables.video_object.write(variables.img)
        
        # Release video object
        variables.video_object.release()
    
    def _draw_masked_object(
        self,
        variables: AnimationVariables,
        object_mask: Optional[np.ndarray] = None,
        skip_rate: int = 5,
        black_pixel_threshold: int = 10
    ):
        """Draw masked object with hand animation"""
        
        img_thresh_copy = variables.img_thresh.copy()
        
        if object_mask is not None:
            object_mask_black_ind = np.where(object_mask == 0)
            object_ind = np.where(object_mask == 255)
            img_thresh_copy[object_mask_black_ind] = 255
        
        selected_ind = 0
        n_cuts_vertical = int(math.ceil(variables.resize_ht / variables.split_len))
        n_cuts_horizontal = int(math.ceil(variables.resize_wd / variables.split_len))
        
        # Cut the image into grids
        grid_of_cuts = np.array(np.split(img_thresh_copy, n_cuts_horizontal, axis=-1))
        grid_of_cuts = np.array(np.split(grid_of_cuts, n_cuts_vertical, axis=-2))
        
        # Find grids with black pixels
        cut_having_black = (grid_of_cuts < black_pixel_threshold) * 1
        cut_having_black = np.sum(np.sum(cut_having_black, axis=-1), axis=-1)
        cut_black_indices = np.array(np.where(cut_having_black > 0)).T
        
        counter = 0
        while len(cut_black_indices) > 1:
            selected_ind_val = cut_black_indices[selected_ind].copy()
            range_v_start = selected_ind_val[0] * variables.split_len
            range_v_end = range_v_start + variables.split_len
            range_h_start = selected_ind_val[1] * variables.split_len
            range_h_end = range_h_start + variables.split_len
            
            temp_drawing = np.zeros((variables.split_len, variables.split_len, 3))
            temp_drawing[:, :, 0] = grid_of_cuts[selected_ind_val[0]][selected_ind_val[1]]
            temp_drawing[:, :, 1] = grid_of_cuts[selected_ind_val[0]][selected_ind_val[1]]
            temp_drawing[:, :, 2] = grid_of_cuts[selected_ind_val[0]][selected_ind_val[1]]
            
            variables.drawn_frame[range_v_start:range_v_end, range_h_start:range_h_end] = temp_drawing
            
            hand_coord_x = range_h_start + int(variables.split_len / 2)
            hand_coord_y = range_v_start + int(variables.split_len / 2)
            
            drawn_frame_with_hand = self._draw_hand_on_img(
                variables.drawn_frame.copy(),
                variables.hand.copy(),
                hand_coord_x,
                hand_coord_y,
                variables.hand_mask_inv.copy(),
                variables.hand_ht,
                variables.hand_wd,
                variables.resize_ht,
                variables.resize_wd
            )
            
            # Update indices
            cut_black_indices[selected_ind] = cut_black_indices[-1]
            cut_black_indices = cut_black_indices[:-1]
            del selected_ind
            
            # Select next index
            euc_arr = euc_dist(cut_black_indices, selected_ind_val)
            selected_ind = np.argmin(euc_arr)
            
            counter += 1
            if counter % skip_rate == 0:
                variables.video_object.write(drawn_frame_with_hand)
        
        if object_mask is not None:
            variables.drawn_frame[:, :, :][object_ind] = variables.img[object_ind]
        else:
            variables.drawn_frame[:, :, :] = variables.img
    
    def _draw_hand_on_img(
        self,
        drawing: np.ndarray,
        hand: np.ndarray,
        drawing_coord_x: int,
        drawing_coord_y: int,
        hand_mask_inv: np.ndarray,
        hand_ht: int,
        hand_wd: int,
        img_ht: int,
        img_wd: int
    ) -> np.ndarray:
        """Draw hand on image"""
        
        remaining_ht = img_ht - drawing_coord_y
        remaining_wd = img_wd - drawing_coord_x
        
        crop_hand_ht = min(hand_ht, remaining_ht)
        crop_hand_wd = min(hand_wd, remaining_wd)
        
        hand_cropped = hand[:crop_hand_ht, :crop_hand_wd]
        hand_mask_inv_cropped = hand_mask_inv[:crop_hand_ht, :crop_hand_wd]
        
        # Apply mask and blend
        for channel in range(3):
            drawing[
                drawing_coord_y:drawing_coord_y + crop_hand_ht,
                drawing_coord_x:drawing_coord_x + crop_hand_wd,
                channel
            ] = (
                drawing[
                    drawing_coord_y:drawing_coord_y + crop_hand_ht,
                    drawing_coord_x:drawing_coord_x + crop_hand_wd,
                    channel
                ] * hand_mask_inv_cropped
            )
        
        drawing[
            drawing_coord_y:drawing_coord_y + crop_hand_ht,
            drawing_coord_x:drawing_coord_x + crop_hand_wd
        ] = (
            drawing[
                drawing_coord_y:drawing_coord_y + crop_hand_ht,
                drawing_coord_x:drawing_coord_x + crop_hand_wd
            ] + hand_cropped
        )
        
        return drawing
    
    def _ffmpeg_convert(self, source_vid: str, dest_vid: str, platform: str = "linux") -> bool:
        """Convert video using ffmpeg"""
        
        try:
            import av
            
            src_path = Path(source_vid)
            input_container = av.open(str(src_path), mode="r")
            output_container = av.open(dest_vid, mode="w")
            
            in_stream = input_container.streams.video[0]
            width = in_stream.codec_context.width
            height = in_stream.codec_context.height
            fps = in_stream.average_rate
            
            out_stream = output_container.add_stream("h264", rate=fps)
            out_stream.width = width
            out_stream.height = height
            out_stream.pix_fmt = "yuv420p"
            out_stream.options = {"crf": "20"}
            
            for frame in input_container.decode(video=0):
                packet = out_stream.encode(frame)
                if packet:
                    output_container.mux(packet)
            
            packet = out_stream.encode(None)
            if packet:
                output_container.mux(packet)
            
            output_container.close()
            input_container.close()
            
            return True
        except Exception as e:
            print(f"FFmpeg conversion error: {e}")
            return False
