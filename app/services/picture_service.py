from app.extensions import db
from app.models.picture import Picture, OrientationEnum
from app.models.datasource import DataSource
from app.models.tag import Tag
from app.services.g_drive_service import GoogleDriveService
from app.utils.image_analysis import analyse_image

import math

class PictureService:

    @staticmethod
    def get_or_create_datasource():
        datasource = DataSource.query.filter_by(name="GOOGLE_DRIVE").first()
        if not datasource:
            datasource = DataSource(
                name="GOOGLE_DRIVE",
                link="https://drive.google.com",
                type="CLOUD_STORAGE",
            )
            db.session.add(datasource)
            db.session.commit()
        return datasource

    @staticmethod
    def compute_orientation(width, height):
        if abs(width - height) < 10:
            return OrientationEnum.SQUARE
        elif width >= height:
            return OrientationEnum.LANDSCAPE
        return OrientationEnum.PORTRAIT

    @staticmethod
    def upload_from_drive(folder_url: str = None):
        selected_fields = "files(id, name, hasThumbnail, thumbnailLink, size, imageMediaMetadata, webContentLink, webViewLink, modifiedTime)"
        g_drive_service = GoogleDriveService().build()
        cmp_pictures_added = 0

        # Extraire le folder_id depuis l'URL
        query = "mimeType contains 'image/'"
        if folder_url:
            folder_id = folder_url.rstrip('/').split('/')[-1]
            query += f" and '{folder_id}' in parents"

        list_file = g_drive_service.files().list(
            fields=selected_fields,
            q=query
        ).execute()

        datasource = PictureService.get_or_create_datasource()

        for file in list_file["files"]:
            if Picture.query.filter_by(google_id=file.get("id")).first():
                continue
            
            if not file.get("hasThumbnail", False):
                continue
            
            metadata = file.get("imageMediaMetadata", {})
            width  = metadata.get("width")
            height = metadata.get("height")

            if not width or not height:
                continue
            
            result = analyse_image(f'https://drive.google.com/thumbnail?id={file.get("id")}&sz=s800')

            image = Picture()
            image.create(
                name=file.get("name"),
                comment=None,
                google_id=file.get("id"),
                tags=[],
                mainColors= result["dom_colors"],
                ratio=0, # TODO
                orientation=PictureService.compute_orientation(width, height),
                resolutionY=height,
                resolutionX=width,
                contrast=0, # TODO
                luminosity= result["avg_luminosity"] ,
                thumbnailLink=f'https://drive.google.com/thumbnail?id={file.get("id")}&sz=s800',
                downloadLink=file.get("webContentLink"),
                lastUpdated=file.get("modifiedTime"),
                datasource_id=datasource.id,
            )
            db.session.add(image)
            cmp_pictures_added += 1

        db.session.commit()
        return cmp_pictures_added

    @staticmethod
    def build_filter_query(args):
        query = Picture.query

        name = args.get("name")
        if name:
            query = query.filter(Picture.name.ilike(f"%{name}%"))

        comment = args.get("comment")
        if comment:
            query = query.filter(Picture.comment.ilike(f"%{comment}%"))

        min_width = args.get("min_width", type=int)
        if min_width is not None:
            query = query.filter(Picture.resolutionX >= min_width)

        max_width = args.get("max_width", type=int)
        if max_width is not None:
            query = query.filter(Picture.resolutionX <= max_width)

        min_height = args.get("min_height", type=int)
        if min_height is not None:
            query = query.filter(Picture.resolutionY >= min_height)

        max_height = args.get("max_height", type=int)
        if max_height is not None:
            query = query.filter(Picture.resolutionY <= max_height)

        orientation = args.get("orientation", type=str)
        if orientation:
            try:
                orientation_enum = OrientationEnum(orientation.lower())
                query = query.filter(Picture.orientation == orientation_enum)
            except ValueError:
                pass  # valeur pas dans l'enum

        tags = args.get("tags")
        if tags:
           tag_ids = [int(t) for t in tags.split(",")] 
           query = query.join(Picture.tags).filter(Tag.id.in_(tag_ids))

        main_colors = args.get("mainColors")
        if main_colors:
            print(main_colors.split(","))
            query = query.filter(Picture.mainColors.op('&&')(main_colors.split(",")))
        
        luminosity = args.get("luminosity")
        if luminosity:
                ## input is between 0-100
                luminosity = (math.floor(float(luminosity))/100) * 255
                ## permissive filter
                print("upper:", luminosity*1.1, ", lower:", luminosity*0.9)
                query = query.filter(Picture.luminosity <= 1.1*luminosity, Picture.luminosity >= 0.9*luminosity)

        updated_after = args.get("updated_after")
        if updated_after:
            query = query.filter(Picture.lastUpdated >= updated_after)

        return query

    @staticmethod
    def update(picture, data):
        picture.name    = data.get("name",    picture.name)
        picture.comment = data.get("comment", picture.comment)

        tag_ids = data.get("tags")
        if tag_ids is not None:
            picture.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

        db.session.commit()
        return picture