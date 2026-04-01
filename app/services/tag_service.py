from app.extensions import db
from app.models.tag import Tag


class TagService:

    @staticmethod
    def get_all(page, per_page):
        return Tag.query.order_by(Tag.id).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def check_duplicate(name):
        return Tag.query.filter_by(name=name).first() is not None

    @staticmethod
    def create(name, hex_code):
        tag = Tag()
        tag.create(name=name, hex_code=hex_code)
        db.session.add(tag)
        db.session.commit()
        return tag

    @staticmethod
    def update(tag, data):
        tag.name     = data.get("name",     tag.name)
        tag.hex_code = data.get("hex_code", tag.hex_code)
        db.session.commit()
        return tag

    @staticmethod
    def delete(tag):
        db.session.delete(tag)
        db.session.commit()
    
    @staticmethod
    def build_tag_filter_query(name):
        query = Tag.query
        
        if name:
            query = query.filter(Tag.name.ilike(f"{name}%"))
        return query