from django.db import connection
from django.db.models.fields import related

class VersionsManyToManyField(related.ManyToManyField):
    def contribute_to_class(self, cls, name):
        super(VersionsManyToManyField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, VersionsReverseManyRelatedObjectsDescriptor(self))

class VersionsReverseManyRelatedObjectsDescriptor(related.ReverseManyRelatedObjectsDescriptor):
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        # Dynamically create a class that subclasses the related
        # model's default manager.
        rel_model=self.field.rel.to
        superclass = rel_model._default_manager.__class__
        RelatedManager = related.create_many_related_manager(superclass, self.field.rel.through)
        class VersionsRelatedManager(RelatedManager):
            def add(self, *args, **kwargs):
                return super(VersionsRelatedManager, self).add(*args, **kwargs)

            def remove(self, *args, **kwargs):
                return super(VersionsRelatedManager, self).remove(*args, **kwargs)

            def clear(self, *args, **kwargs):
                return super(VersionsRelatedManager, self).clear(*args, **kwargs)

        qn = connection.ops.quote_name
        manager = VersionsRelatedManager(
            model=rel_model,
            core_filters={'%s__pk' % self.field.related_query_name(): instance._get_pk_val()},
            instance=instance,
            symmetrical=self.field.rel.symmetrical,
            join_table=qn(self.field.m2m_db_table()),
            source_col_name=qn(self.field.m2m_column_name()),
            target_col_name=qn(self.field.m2m_reverse_name())
        )
        manager.reverse_model_instance = instance
        return manager