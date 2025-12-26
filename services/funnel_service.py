import logging
from typing import Optional, List
from datetime import datetime
from database.models import Funnel, FunnelStep
from utils.db import SessionLocal

logger = logging.getLogger(__name__)

class FunnelService:
    @staticmethod
    def create_funnel(owner_id: str, name: str, funnel_type: str = "onboarding") -> Optional[Funnel]:
        db = SessionLocal()
        try:
            funnel = Funnel(
                owner_id=owner_id,
                name=name,
                funnel_type=funnel_type,
                status="draft"
            )
            db.add(funnel)
            db.commit()
            db.refresh(funnel)
            logger.info(f"Created funnel: {funnel.id} for owner {owner_id}")
            return funnel
        except Exception as e:
            logger.error(f"Error creating funnel: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_funnel(funnel_id: int) -> Optional[Funnel]:
        db = SessionLocal()
        try:
            return db.query(Funnel).filter(Funnel.id == funnel_id).first()
        finally:
            db.close()
    
    @staticmethod
    def get_funnels_by_owner(owner_id: str) -> List[Funnel]:
        db = SessionLocal()
        try:
            return db.query(Funnel).filter(Funnel.owner_id == owner_id).all()
        finally:
            db.close()
    
    @staticmethod
    def get_all_funnels() -> List[Funnel]:
        db = SessionLocal()
        try:
            return db.query(Funnel).all()
        finally:
            db.close()
    
    @staticmethod
    def update_funnel(funnel_id: int, **kwargs) -> bool:
        db = SessionLocal()
        try:
            funnel = db.query(Funnel).filter(Funnel.id == funnel_id).first()
            if not funnel:
                return False
            for key, value in kwargs.items():
                if hasattr(funnel, key):
                    setattr(funnel, key, value)
            funnel.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating funnel: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_funnel(funnel_id: int) -> bool:
        db = SessionLocal()
        try:
            db.query(FunnelStep).filter(FunnelStep.funnel_id == funnel_id).delete()
            result = db.query(Funnel).filter(Funnel.id == funnel_id).delete()
            db.commit()
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting funnel: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def add_step(funnel_id: int, content: str, title: str = None, photo_file_id: str = None) -> Optional[FunnelStep]:
        db = SessionLocal()
        try:
            last_order = db.query(FunnelStep).filter(FunnelStep.funnel_id == funnel_id).count()
            step = FunnelStep(
                funnel_id=funnel_id,
                step_order=last_order + 1,
                title=title,
                content=content,
                photo_file_id=photo_file_id
            )
            db.add(step)
            funnel = db.query(Funnel).filter(Funnel.id == funnel_id).first()
            if funnel:
                funnel.steps_count = last_order + 1
            db.commit()
            db.refresh(step)
            return step
        except Exception as e:
            logger.error(f"Error adding step: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_steps(funnel_id: int) -> List[FunnelStep]:
        db = SessionLocal()
        try:
            return db.query(FunnelStep).filter(FunnelStep.funnel_id == funnel_id).order_by(FunnelStep.step_order).all()
        finally:
            db.close()
    
    @staticmethod
    def update_step(step_id: int, **kwargs) -> bool:
        db = SessionLocal()
        try:
            step = db.query(FunnelStep).filter(FunnelStep.id == step_id).first()
            if not step:
                return False
            for key, value in kwargs.items():
                if hasattr(step, key):
                    setattr(step, key, value)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating step: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_step(step_id: int) -> bool:
        db = SessionLocal()
        try:
            step = db.query(FunnelStep).filter(FunnelStep.id == step_id).first()
            if step:
                funnel_id = step.funnel_id
                db.delete(step)
                remaining = db.query(FunnelStep).filter(FunnelStep.funnel_id == funnel_id).order_by(FunnelStep.step_order).all()
                for i, s in enumerate(remaining):
                    s.step_order = i + 1
                funnel = db.query(Funnel).filter(Funnel.id == funnel_id).first()
                if funnel:
                    funnel.steps_count = len(remaining)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting step: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def increment_views(funnel_id: int):
        db = SessionLocal()
        try:
            funnel = db.query(Funnel).filter(Funnel.id == funnel_id).first()
            if funnel:
                funnel.views_count = (funnel.views_count or 0) + 1
                db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def increment_conversions(funnel_id: int):
        db = SessionLocal()
        try:
            funnel = db.query(Funnel).filter(Funnel.id == funnel_id).first()
            if funnel:
                funnel.conversions = (funnel.conversions or 0) + 1
                db.commit()
        except:
            db.rollback()
        finally:
            db.close()

funnel_service = FunnelService()
